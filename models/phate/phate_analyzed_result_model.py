from models.analyzed_result_model import AnalyzedResultModel
from typing import Dict, Tuple, Callable, List, Any
import numpy as np
from numpy import ndarray

class PHATEAnalyzedResultModel(AnalyzedResultModel):
    def __init__(self, result: Dict[Tuple, List[np.ndarray]], current_state):
        super().__init__(result, current_state)
        self.original_data: Dict[Tuple, List[np.ndarray]] = {}
        self.index_to_key: Dict[int, Tuple[int, int, int, float]] = {}
        self.max_centrals: int = 50
        self.eigen_centrals = np.array([])
        self.sorted_centrals: List[int] = []
        self.eigen_values: ndarray[Any] = np.array([])
        self.eigen_vectors: ndarray[Any] = np.array([])
        self.top_low_centrals: List[int] = []
        self.distinct_indices: List[int] = []
        self.distinct_low_centrals: List[int] = []
        self.past_selected_indices: List[int] = []
        self.past_selected_keys: List[Tuple[int, int, int, float]] = []
        self.past_selected_structures: Dict[Tuple[int, int, int, float], List[ndarray]] = {}

    def from_map(self, map: Dict[str, Any]):
        self.original_data = map['original_data']
        self.index_to_key = map['index_to_key']
        self.max_centrals = map['max_centrals']
        self.eigen_centrals = map['eigen_centrals']
        self.sorted_centrals = map['sorted_centrals']
        self.eigen_values = map['eigen_values']
        self.eigen_vectors = map['eigen_vectors']
        self.top_low_centrals = map['top_low_centrals']
        self.distinct_indices = map['distinct_indices']
        self.distinct_low_centrals = map['distinct_low_centrals']
        self.past_selected_keys = map['past_selected_keys'] if 'past_selected_keys' in map else []
        self.past_selected_structures = map['past_selected_structures'] if 'past_selected_structures' in map else {}
        self.past_selected_indices = map['past_selected_indices'] if 'past_selected_indices' in map else []
        return self
