from typing import Dict, Tuple, List
from mdtraj import Trajectory, Topology
from .base_result_model import BaseResultModel
import numpy as np

class MDResultModel(BaseResultModel):
    def __init__(self, result: Dict[Tuple[int, int, int, float], List[np.ndarray]], current_state: Tuple[int, int], md_settings: Dict[str, object]):
        super().__init__(result)
        '''
        result: Dict[Tuple[int, int, int, float], List[np.ndarray]]
        current_state: Tuple[int, int]
        result includes a few past trajectories and current trajectories.
        '''
        self.current_state = current_state
        self.md_settings = md_settings

    def get_current_result(self) -> Dict[Tuple[int, int, int, float], List[np.ndarray]]:
        current_result = {}
        current_keys = set(filter(set(self.result.keys()), lambda x: x[0] == self.current_state[0] and x[1] == self.current_state[1]))
        for key in current_keys:
            current_result[key] = self.result[key]
        return current_result
