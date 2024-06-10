from typing import Dict
from models import EvaluatedResultModel
from models.analyzed_result_model import AnalyzedResultModel
from models.phate.phate_analyzed_result_model import PHATEAnalyzedResultModel
from ..i_evaluater import IEvaluater
import random


class PHATEEvaluter(IEvaluater):
    def __init__(self):
        self.analyzed_result_model = None
        self.is_continue = None
        self.max_central_list = None

    def evaluate(self) -> bool:

        if self.analyzed_result_model is None:
            raise ValueError("Analyzed result model is not set.")

        current_cycle = self.analyzed_result_model.current_state[1]
        if current_cycle <= self.threshold:
            self.is_continue = True
            return True
        else:
            self.is_continue = False
            return False

    def set_analyzed_result(self, analyzed_result_model: PHATEAnalyzedResultModel) -> None:
        self.analyzed_result_model = analyzed_result_model

    def set_configuration(self, configuration: Dict[str, object]) -> None:
        self.threshold = configuration['threshold']
