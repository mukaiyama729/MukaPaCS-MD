import abc
from typing import Dict, Tuple, List
from models import EvaluatedResultModel, AnalyzedResultModel

class ISelector(metaclass=abc.Meta):

    @abc.abstractmethod
    def select(self) -> List[Tuple[int, int, int, float]]:
        pass

    @abc.abstractmethod
    def set_analyzed_result_model(self, analyzed_result: AnalyzedResultModel) -> None:
        pass

    @abc.abstractmethod
    def set_configuration(self, configuration: Dict[str, object]) -> None:
        pass
