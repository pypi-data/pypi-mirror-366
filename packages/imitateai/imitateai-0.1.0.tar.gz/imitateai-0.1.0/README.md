# ImitateAI: Inverse Reinforcement Learning for LLMs

[![PyPI version](https://badge.fury.io/py/rewardinfer.svg)](https://badge.fury.io/py/rewardinfer)
[![Build Status](https://travis-ci.org/your-username/rewardinfer.svg?branch=master)](https://travis-ci.org/your-username/rewardinfer)
[![Documentation Status](https://readthedocs.org/projects/rewardinfer/badge/?version=latest)](https://rewardinfer.readthedocs.io/en/latest/?badge=latest)

`ImitateAI` is a Python package for applying Inverse Reinforcement Learning (IRL) techniques to Large Language Models (LLMs). It provides a simple and intuitive interface for researchers and developers to infer the implicit reward functions of aligned LLMs and to iteratively refine LLMs using these inferred rewards.

The core idea is to understand and replicate the alignment of an LLM by observing its behavior (i.e., its generated text) and then using that understanding to further improve it. This library streamlines the process, making cutting-edge IRL algorithms accessible.

## Key Features

*   **Reward Model Inference**: Easily obtain a set of reward models from an aligned LLM hosted on the Hugging Face Hub. `ImitateAI` implements multiple state-of-the-art IRL algorithms to give you a comprehensive view of the model's learned preferences.
*   **Recursive Refinement Loop**: Implement a powerful IRL -> RL -> IRL loop to recursively refine your LLMs. This iterative process allows you to continuously improve your model's alignment based on the inferred reward functions.
*   **Hugging Face Integration**: Seamlessly works with models from the Hugging Face Hub, allowing you to leverage thousands of pre-trained and aligned LLMs.
*   **Simple & Modular Design**: The library is designed to be intuitive and extensible, following best practices from well-known ML libraries like `transformers` and `stable-baselines`.

## Installation

You can install `ImitateAI` directly from PyPI:

```bash
pip install imitateai
```

Make sure you have PyTorch installed. You can find installation instructions for your specific setup on the [PyTorch website](https://pytorch.org/).

## Quick Start

Here’s how you can get started with the two main use cases of `ImitateAI`.

### Use Case 1: Obtain Reward Models from an Aligned LLM

This use case allows you to take an existing, aligned LLM from the Hugging Face Hub and extract a set of reward models that represent its learned preferences.

```python
from imitateai import RewardModeler
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. Specify the aligned LLM you want to analyze from Hugging Face
aligned_model_id = "meta-llama/Llama-2-7b-chat-hf"

# 2. Initialize the RewardModeler with the model ID
modeler = RewardModeler(model_id=aligned_model_id)

# 3. Infer the reward models
# This will use 3 different IRL methods to generate k=1 reward model each by default.
# The methods are: Maximum Entropy IRL, Maximum Causal Entropy IRL, and GAIL.
reward_models = modeler.infer_reward_models(k=1)

# 4. Access your reward models
# The output is a dictionary where keys are the IRL method names
# and values are the trained reward models.
for method, models in reward_models.items():
    print(f"Method: {method}")
    for i, rm in enumerate(models):
        print(f"  - Reward Model {i+1} saved at: {rm.save_path}")

# You can now use these reward models for analysis or for the next use case.
```

### Use Case 2: Recursive IRL -> RL -> IRL Refinement

This use case demonstrates how to take a base LLM and iteratively refine it. In each iteration, we first infer a reward model (IRL) and then fine-tune the LLM using that reward model (RL).

```python
from imitateai import RecursiveRefiner

# 1. Specify a base LLM to start the refinement process
# This can be a pre-trained model or a model you've already aligned.
base_model_id = "EleutherAI/gpt-neo-1.3B"

# 2. Initialize the RecursiveRefiner
refiner = RecursiveRefiner(model_id=base_model_id)

# 3. Run the recursive refinement process for a specified number of iterations
# The `refine` method will handle the IRL -> RL loop internally.
refined_model = refiner.refine(iterations=3)

# 4. The refined model is returned after the final iteration
# You can now use it or push it to the Hugging Face Hub.
print(f"Refined model is ready to use: {refined_model}")

# To save your final model:
refined_model.save_pretrained("./my-refined-model")
```

## How It Works

`ImitateAI` is built upon the idea that an aligned LLM's outputs (demonstrations) implicitly contain information about the reward function it was optimized for.

1.  **Inverse Reinforcement Learning (IRL)**: We use algorithms like Maximum Entropy IRL, GAIL (Generative Adversarial Imitation Learning), and others to "reverse-engineer" a reward model from the demonstrations provided by the aligned LLM. These methods aim to find a reward function under which the expert's (the LLM's) behavior is optimal.

2.  **Reinforcement Learning (RL)**: Once a reward model is inferred, we use it to further fine-tune the LLM. This is done using a policy gradient algorithm (like PPO) where the inferred reward model provides the signal for what constitutes "good" behavior.

The recursive nature of Use Case 2 allows for a continuous cycle of improvement, where the LLM becomes more and more aligned with the desired (but initially unknown) reward function.

## Contributing

We welcome contributions! If you'd like to help improve `ImitateAI`, please check out our contributing guidelines and open an issue or pull request on our [GitHub repository](https://github.com/your-username/rewardinfer).

## Citation

If you use `ImitateAI` in your research, please consider citing our work. (Citation details to be added).

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.