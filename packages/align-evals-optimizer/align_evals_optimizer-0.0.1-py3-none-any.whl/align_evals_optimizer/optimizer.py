from langchain_core.load import dumpd
import langsmith
import os
import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
import time
from langchain_core.prompts import ChatPromptTemplate
import json

def format_meta_prompt(sample_example, current_prompt, incorrect_examples):
    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, 'prompt.txt'), 'r') as file:
        system_prompt = file.read()

    prompt = [("system", system_prompt), ("user",
    f"Here is the sample example to see what variables are available to you:{sample_example}\n\nHere is the current prompt:\n{current_prompt}\n\n\Here are the examples that were incorrectly aligned:\n{incorrect_examples}")]
    
    return prompt

def get_variables_from_input_variables(input_variables, inputs):
    variables = {}
    for input_variable in input_variables:
        keys = input_variable.split('.')
        value = inputs
        for key in keys:
            value = value[key]
        variables[input_variable] = value
    return variables

def format_experiment_results(current_prompt, experiment_results, client, input_only=False, max_examples=10):
    # max_examples introduced because token limit
    if not input_only:
        print(f"There are {len(experiment_results)} misaligned examples")
    result = ""
    for experiment_result in experiment_results[:max_examples]:
        result += f"<example>\n<input>\n{get_variables_from_input_variables(current_prompt.input_variables, experiment_result.inputs['inputs']) if not input_only else experiment_result.inputs['inputs']}</input>"
        if input_only:
            result += f"\n</example>"
        else:
            reference_example = client.read_example(example_id=experiment_result.reference_example_id)
            result += f"\n<reference_outputs>\n{reference_example.outputs}</reference_outputs>\n</example>\n\n"

    return result


class Messages(BaseModel):
    messages: list[tuple[str, str]] = Field(..., description="New messages for the prompt to use. The messages are a list of [role, content], where role is either 'system' (only the first message), 'user', or 'ai'")

@tool
def generate_new_messages(messages: Messages):
    """
    Update the messages used by the prompt
    """
    return None

class Optimizer:
    def __init__(self, model="anthropic:claude-opus-4-20250514", langsmith_api_key = os.environ.get("LANGSMITH_API_KEY"), langsmith_url = os.environ.get("LANGSMITH_URL"), max_examples=10):
        self.model = model
        self.langsmith_api_key = langsmith_api_key
        self.langsmith_url = langsmith_url or "https://api.smith.langchain.com"

        self.client = langsmith.Client(api_key=self.langsmith_api_key, api_url=self.langsmith_url)
        self.model = init_chat_model(model=model).bind_tools([generate_new_messages], tool_choice="generate_new_messages")
        self.max_examples = max_examples

    def optimize_aligned_evaluator(self, evaluator_id, max_iterations = 3, stop_threshold = 0.95):
        #TODO: throw a better error
        evaluator = requests.get(f"{self.langsmith_url}/api/v1/runs/rules?id={evaluator_id}", headers={"x-api-key": self.langsmith_api_key}).json()[0]

        if not evaluator["evaluator_version"] >= 3:
            raise ValueError("Evaluator must be alignable. Read the docs to learn more: https://docs.smith.langchain.com/evaluation/tutorials/aligning_evaluator")

        correction_dataset_id = evaluator["corrections_dataset_id"]
        correction_dataset = self.client.read_dataset(dataset_id=correction_dataset_id)
        if not correction_dataset or not correction_dataset.example_count > 0:
            raise ValueError("Correction dataset is empty or does not exist. Read here to learn about how to annotate examples for an aligned evaluator: https://docs.smith.langchain.com/evaluation/tutorials/aligning_evaluator#2-label-examples")

        #TODO: get baseline score somehow
        current_prompt_ref = evaluator["evaluators"][0]["structured"]["hub_ref"]
        variable_mapping = evaluator["evaluators"][0]["structured"]["variable_mapping"]
        prompt_name = current_prompt_ref.split(":")[0]
        current_prompt_and_model = self.client.pull_prompt(current_prompt_ref, include_model=True)
        current_prompt_info = self.client.get_prompt(prompt_name)
        current_prompt_owner = current_prompt_info.owner
        current_prompt_commit_hash = current_prompt_info.last_commit_hash
        model = current_prompt_and_model.middle[0].bound
        current_prompt = current_prompt_and_model.first
        feedback_key = [k for k in current_prompt.schema_["properties"].keys() if k != "comment"][0]
        
        def alignment_evaluator(outputs, reference_outputs):
            return {"key": "offline_alignment", "score": int(outputs[feedback_key] == reference_outputs[feedback_key])}

        iteration = 1
        alignment_score = 0
        print("Running alignment experiments...")
        while iteration <= max_iterations and alignment_score < stop_threshold:
            def target(inputs):
                input_variables = [
                    variable_mapping[k] if k in variable_mapping else k
                    for k in current_prompt.input_variables
                ]
                variables = get_variables_from_input_variables(input_variables, inputs)
                
                chain = current_prompt | model
                result = chain.invoke(variables)
                return {feedback_key: result[feedback_key], **({"comment": result["comment"]} if "comment" in result else {})}
            
            response = self.client.evaluate(
                target,
                data=correction_dataset.name,
                evaluators=[alignment_evaluator],
                max_concurrency=8
            )
            experiment_name = response.experiment_name
            time.sleep(3)

            alignment_experiment_results = [r for r in self.client.list_runs(project_name=experiment_name, is_root=True)]
            message_generation_iteration = 0
            while message_generation_iteration < 2:
                prompt = format_meta_prompt(
                    format_experiment_results(current_prompt, alignment_experiment_results[:1], self.client, input_only=True),
                    current_prompt,
                    format_experiment_results(current_prompt, [r for r in alignment_experiment_results if ((r.feedback_stats or {}).get('offline_alignment') or {}).get('avg') == 0], self.client, max_examples=self.max_examples)
                )
                new_prompt = self.model.invoke(prompt)
                try:
                    messages = json.loads(new_prompt.tool_calls[0]['args']['messages'], strict=False) if isinstance(new_prompt.tool_calls[0]['args']['messages'], str) else new_prompt.tool_calls[0]['args']['messages']['messages']
                    break
                except:
                    print("Failed to parse updated messages, attempting once more")
                message_generation_iteration += 1
            current_prompt_and_model.first.messages = ChatPromptTemplate([tuple(message) for message in messages]).messages
            current_prompt = current_prompt_and_model.first
            serialized_prompt_and_model = dumpd(current_prompt_and_model)
            response =requests.post(f"{self.langsmith_url}/commits/{current_prompt_owner}/{prompt_name}", headers={"x-api-key": self.langsmith_api_key},
                json={"manifest": {"lc": 1, "type": "constructor", "id": ["langsmith", "playground", "PromptPlayground"], "kwargs": {"first": serialized_prompt_and_model["kwargs"]["first"], "last": dumpd(model)}}, "parent_commit": current_prompt_commit_hash, "skip_webhooks": []})
            current_prompt_commit_hash = response.json()['commit']['commit_hash']
            alignment_score = sum([r.feedback_stats['offline_alignment']['avg'] for r in alignment_experiment_results if r.feedback_stats])/len([r for r in alignment_experiment_results if r.feedback_stats])
            print(f"Iteration {iteration} Alignment Score: {alignment_score}")
            iteration += 1


        
