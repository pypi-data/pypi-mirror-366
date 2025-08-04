import torch
import torch.nn as nn
from transformers import AutoModel, PreTrainedModel

class RewardModel(PreTrainedModel):
    """
    A reward model that outputs a scalar reward for a given text sequence.
    It consists of a base transformer model and a linear head.
    """
    def __init__(self, config, base_model_id: str):
        super().__init__(config)
        self.transformer = AutoModel.from_pretrained(base_model_id)
        # The reward head
        self.reward_head = nn.Linear(self.transformer.config.hidden_size, 1, bias=False)

    def forward(self, input_ids, attention_mask=None, **kwargs):
        """
        Forward pass to compute the reward.
        
        Returns a scalar reward for each sequence in the batch.
        """
        # Get the hidden states from the base model
        outputs = self.transformer(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            **kwargs
        )
        
        # Use the hidden state of the last token
        last_hidden_state = outputs.last_hidden_state
        eos_indices = attention_mask.sum(dim=1) - 1
        pooled_output = last_hidden_state[torch.arange(len(last_hidden_state)), eos_indices]

        # Pass through the reward head
        reward = self.reward_head(pooled_output)
        return reward