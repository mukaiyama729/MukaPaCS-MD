from .base_result_model import BaseResultModel
from typing import Dict, Tuple, List

class EvaluatedResultModel(BaseResultModel):
    def __init__(self, result: Dict[Tuple[int, int, int, float], List[float]], current_state: Tuple[int, int], **kwargs):
        super().__init__(result)
        self.current_state = current_state
        for key, value in kwargs.items():
            setattr(self, key, value)
