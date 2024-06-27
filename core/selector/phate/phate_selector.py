from typing import Dict
from ..i_selector import ISelector
from models.phate import PHATEAnalyzedResultModel
from models.phate.phate_analyzed_result_model import PHATEAnalyzedResultModel
from typing import List, Tuple, Dict
import random
from numpy import ndarray
import numpy as np
import logging

logger = logging.getLogger('pacs_md')

class PHATESelector(ISelector):
    def __init__(self):
        self.analyzed_result_model: PHATEAnalyzedResultModel = None
        self.is_continue: bool = None
        self.max_central_list: List[int] = None
        self._past_selected_structures: Dict[Tuple[int, int, int, float], List[np.ndarray]] = {}
        self.how_many: int = 30

    def select(self) -> List[Tuple[int, int, int, float]]:
        if self.analyzed_result_model is None:
            raise ValueError("Analyzed result model is not set.")

        dlc_len = len(self.analyzed_result_model.distinct_low_centrals)

        if dlc_len < self.how_many:
            self.max_central_list = self.analyzed_result_model.distinct_low_centrals + random.sample(self.analyzed_result_model.top_low_centrals, self.how_many - dlc_len)
        else:
            self.max_central_list = self.analyzed_result_model.distinct_low_centrals

        all_keys = list(self.analyzed_result_model.result.keys())
        result = [all_keys[i] for i in self.max_central_list]
        self._update_past_structures()
        return result

    def _update_past_structures(self):
        logger.info('update past selected structures')
        all_keys = list(self.analyzed_result_model.original_data.keys())
        for index in self.max_central_list:
            self._past_selected_structures[all_keys[index]] = self.analyzed_result_model.original_data[all_keys[index]]

    def past_selected_structures(self) -> Dict[Tuple[int, int, int, float], List[np.ndarray]]:
        return self._past_selected_structures

    def set_analyzed_result_model(self, analyzed_result_model: PHATEAnalyzedResultModel) -> None:
        self.analyzed_result_model = analyzed_result_model

    def set_configuration(self, configuration: Dict[str, object]) -> None:
        self.how_many = configuration['how_many']
