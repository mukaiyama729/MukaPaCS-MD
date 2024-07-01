import abc
from typing import Dict, Tuple, List
from models import AnalyzedResultModel
from numpy import ndarray

class IVisualizer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def visualize(self) -> None:
        pass

    @abc.abstractmethod
    def set_configuration(self, configuration: Dict[str, object]) -> None:
        pass

    @abc.abstractmethod
    def set_analyzed_result_model(self, analyzed_result: AnalyzedResultModel) -> None:
        pass
