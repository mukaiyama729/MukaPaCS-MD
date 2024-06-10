from typing import Dict
from ..i_selector import ISelector
from models import AnalyzedResultModel
from models.phate.phate_analyzed_result_model import PHATEAnalyzedResultModel
from typing import List, Tuple, Dict
import random


class PHATESelector(ISelector):
    def __init__(self):
        self.analyzed_result_model = None
        self.is_continue = None
        self.max_central_list: List[int] = None

    def select(self) -> List[Tuple[int, int, int, float]]:
        if self.analyzed_result_model is None:
            raise ValueError("Analyzed result model is not set.")

        dlc_len = len(self.analyzed_result_model.distinct_low_centrals)

        if dlc_len < self.analyzed_result_model.max_centrals:
            self.max_central_list = self.analyzed_result_model.distinct_low_centrals + random(self.analyzed_result_model.distinct_indices, self.analyzed_result_model.max_centrals - dlc_len)
        else:
            self.max_central_list = self.analyzed_result_model.distinct_low_centrals

        all_keys = list(self.analyzed_result_model.result.keys())
        result = [all_keys[i] for i in self.max_central_list]
        return result

    def set_analyzed_result(self, analyzed_result_model: PHATEAnalyzedResultModel) -> None:
        self.analyzed_result_model = analyzed_result_model

    def set_configuration(self, configuration: Dict[str, object]) -> None:
        self.how_many = configuration['how_many']
