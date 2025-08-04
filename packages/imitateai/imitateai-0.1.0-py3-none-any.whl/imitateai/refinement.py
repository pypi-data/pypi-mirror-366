# Implements Use Case 2: RecursiveRefiner
from typing import Optional
from transformers import PreTrainedModel
from .modeling import RewardModeler
from .rl.ppo_trainer import PPOTrainer

class RecursiveRefiner:
    """
    Manages the recursive refinement loop of IRL -> RL -> IRL.

    This class takes a base LLM and iteratively improves it by first inferring
    its implicit reward, then enhancing the model with RL using that reward.
    """
    def __init__(self, model_id: str, device: Optional[str] = "cuda"):
        """
        Initializes the RecursiveRefiner with a base LLM.

        Args:
            model_id (str): The Hugging Face model ID of the base LLM to be refined.
            device (str): The device to run the models on ('cuda' or 'cpu').
        """
        self.base_model_id = model_id
        self.device = device

    def refine(self, iterations: int = 3) -> PreTrainedModel:
        """
        Runs the iterative refinement process.

        Args:
            iterations (int): The number of IRL -> RL cycles to perform.

        Returns:
            PreTrainedModel: The final, refined LLM after all iterations.
        """
        current_model_id = self.base_model_id
        print(f"Starting recursive refinement for {iterations} iterations...")

        for i in range(iterations):
            print(f"\n===== Iteration {i+1}/{iterations} =====")
            
            # --- IRL Step ---
            print(f"Step 1: Inferring reward from model '{current_model_id}'")
            modeler = RewardModeler(model_id=current_model_id, device=self.device)
            # For refinement, we typically infer a single reward model
            inferred_rewards = modeler.infer_reward_models(k=1, methods=['gail'])
            # We'll just use the first GAIL reward model for this example
            reward_model = inferred_rewards['gail'][0]
            print("Reward model inferred successfully.")

            # --- RL Step ---
            print("Step 2: Refining the policy model with PPO")
            ppo_trainer = PPOTrainer(
                model_id=current_model_id, 
                reward_model=reward_model, 
                device=self.device
            )
            refined_model = ppo_trainer.train()
            print("Policy model refined successfully.")

            # For the next iteration, the refined model becomes the new expert
            # We save it temporarily and update the model_id
            temp_model_path = f"./temp_model_iter_{i+1}"
            refined_model.save_pretrained(temp_model_path)
            current_model_id = temp_model_path
        
        print("\nRecursive refinement complete.")
        # Load the final model before returning
        final_model = AutoModelForCausalLM.from_pretrained(current_model_id)
        return final_model