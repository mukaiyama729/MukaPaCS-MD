import abc
from typing import Dict, Tuple, List
from models import BaseResultModel, AnalyzedResultModel


class IEvaluater(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def evaluate(self) -> bool:
        pass

    @abc.abstractmethod
    def set_analyzed_result_model(self, analyzed_result: AnalyzedResultModel) -> None:
        pass

    @abc.abstractmethod
    def set_configuration(self, configuration: Dict[str, object]) -> None:
        pass
