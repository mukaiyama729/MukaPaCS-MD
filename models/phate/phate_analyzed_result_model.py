from models.analyzed_result_model import AnalyzedResultModel
from typing import Dict, Tuple, Callable, List, Any
import numpy as np
from numpy import ndarray

class PHATEAnalyzedResultModel(AnalyzedResultModel):
    def __init__(self, result: Dict[Tuple, object], current_state):
        super().__init__(result, current_state)
        self.max_centrals: int = 50
        self.eigen_centrals = np.array([])
        self.sorted_centrals = np.array([])
        self.eigen_values: ndarray[Any] = np.array([])
        self.eigen_vectors: ndarray[Any] = np.array([])
        self.top_low_centrals: ndarray[int] = np.array([])
        self.distinct_indices: List[int] = []
        self.distinct_low_centrals: List[int] = []

    def from_map(self, map: Dict[str, Any]):
        self.max_centrals = map['max_centrals']
        self.eigen_centrals = map['eigen_centrals']
        self.sorted_centrals = map['sorted_centrals']
        self.eigen_values = map['eigen_values']
        self.eigen_vectors = map['eigen_vectors']
        self.top_low_centrals = map['top_low_centrals']
        self.distinct_indices = map['distinct_indices']
        self.distinct_low_centrals = map['distinct_low_centrals']
        return self
