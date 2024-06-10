import abc
from typing import Dict, Tuple, List
from models import MDResultModel, BaseResultModel, AnalyzedResultModel
import numpy as np


class IAnalyzer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def analyze(self) -> AnalyzedResultModel:
        pass

    @abc.abstractmethod
    def set_md_result(self, md_result: MDResultModel) -> None:
        pass

    @abc.abstractmethod
    def set_configuration(self, configuration: Dict[str, object]) -> None:
        pass
