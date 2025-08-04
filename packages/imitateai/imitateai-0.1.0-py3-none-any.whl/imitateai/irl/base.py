from abc import ABC, abstractmethod
from typing import List, Dict
from ..models.reward_model import RewardModel

class AbstractIRLTrainer(ABC):
    """
    Abstract Base Class for all Inverse Reinforcement Learning algorithms.
    """
    def __init__(self, model_id: str, tokenizer, device: str):
        self.model_id = model_id
        self.tokenizer = tokenizer
        self.device = device

    @abstractmethod
    def train(self, demonstrations: List[Dict]) -> RewardModel:
        """
        Trains a reward model based on expert demonstrations.

        Args:
            demonstrations (List[Dict]): A list of expert demonstrations, where
                                         each item contains 'prompt' and 'response'.

        Returns:
            RewardModel: A trained instance of the RewardModel.
        """
        pass