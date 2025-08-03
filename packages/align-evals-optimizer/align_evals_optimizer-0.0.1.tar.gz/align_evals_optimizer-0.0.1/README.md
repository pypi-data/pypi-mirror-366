# Align Evals Optimizer

This is a simple python package that optimizes the prompts for your LangSmith aligned evaluators.

## Prerequisites

Follow the docs (here)[https://docs.smith.langchain.com/evaluation/tutorials/aligning_evaluator] to create an alignable evaluator.

::: note
You don't need to edit your prompt at all from the default, the optimizer will take care of making the prompt as optimized as possible.
:::

## Usage

You can use the optimizer like this:

```python
from align_evals_optimizer import Optimizer

# model must be in provider:model_name format
# max_examples is the maximum number of misaligned examples the prompt optimizer will use to update the prompt
optimizer = Optimizer(model="anthropic:claude-opus-4-20250514", langsmith_api_key="your_langsmith_api_key", langsmith_url="your_langsmith_url", max_examples=5)
optimizer.optimize_aligned_evaluator(evaluator_id="evaluator_id")
```

The optimizer will automatically create new commits every iteration of the optimization process. By going to the reference dataset of the evaluator you are aligning you should be able to see experiments come in as the optimizer runs them, hopefully with an increasing alignment score.


## Future work

This is a very very incomplete package, more done as a thought exercise than anything else.

This is not an exhaustive list but here are some future improvements that I think would be helpful:

- Make less brittle (there are lot's of cases not accounted for)
- Make the code more performant (no async code right now, no parallelization)
- Optimize across multiple models