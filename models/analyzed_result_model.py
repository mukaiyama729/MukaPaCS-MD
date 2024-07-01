from .base_result_model import BaseResultModel
from typing import Dict, Tuple, Callable


class AnalyzedResultModel(BaseResultModel):
    def __init__(self, result: Dict[Tuple, object], current_state: Tuple[int, int]):
        super().__init__(result)
        self.current_state = current_state
