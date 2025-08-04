# Implements Use Case 1: RewardModeler
from typing import Dict, List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from .models.reward_model import RewardModel
from .data.demonstration import generate_demonstrations
from .irl import IRL_ALGORITHMS # This would map strings to IRL classes

class RewardModeler:
    """
    Orchestrates the process of inferring reward models from an aligned LLM.

    This class handles loading the expert model, generating demonstration data,
    and running various IRL algorithms to produce a set of reward models.
    """
    def __init__(self, model_id: str, device: Optional[str] = "cuda"):
        """
        Initializes the RewardModeler with an expert LLM.

        Args:
            model_id (str): The Hugging Face model ID of the aligned "expert" LLM.
            device (str): The device to run the models on ('cuda' or 'cpu').
        """
        self.model_id = model_id
        self.expert_model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        print(f"Expert model '{model_id}' loaded on {self.device}.")

    def infer_reward_models(
        self,
        k: int = 1,
        methods: Optional[List[str]] = None,
        dataset_name: str = "some/prompt/dataset"
    ) -> Dict[str, List[RewardModel]]:
        """
        Infers k reward models for each specified IRL method.

        Args:
            k (int): The number of reward models to train for each method.
            methods (List[str], optional): A list of IRL methods to use.
                Defaults to ['maxent', 'gail', 'adversarial'].
            dataset_name (str): The name of a dataset on Hugging Face to use for prompts.

        Returns:
            Dict[str, List[RewardModel]]: A dictionary mapping method names to a
                                          list of trained RewardModel instances.
        """
        if methods is None:
            methods = ['maxent', 'gail', 'adversarial'] # Default methods

        print("Step 1: Generating expert demonstrations...")
        demonstrations = generate_demonstrations(
            self.expert_model, self.tokenizer, dataset_name
        )

        all_reward_models = {}
        for method_name in methods:
            print(f"\n--- Running IRL method: {method_name} ---")
            if method_name not in IRL_ALGORITHMS:
                print(f"Warning: Method '{method_name}' not found. Skipping.")
                continue

            method_reward_models = []
            for i in range(k):
                print(f"Training reward model {i+1}/{k}...")
                irl_trainer_class = IRL_ALGORITHMS[method_name]
                
                # Each trainer takes the base model info to create a reward model architecture
                irl_trainer = irl_trainer_class(self.model_id, self.tokenizer, self.device)
                
                # The train method returns a trained RewardModel instance
                reward_model = irl_trainer.train(demonstrations)
                method_reward_models.append(reward_model)
            
            all_reward_models[method_name] = method_reward_models
        
        print("\nReward model inference complete.")
        return all_reward_models