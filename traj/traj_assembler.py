from mdtraj import Trajectory, Topology
from typing import Dict, Tuple, List
import numpy as np
from numpy import ndarray
from models import MDResultModel
from utils import Singleton


class TrajAssembler(Singleton):
    def __init__(self, traj_data: Dict[Tuple[int, int, int, float], List[ndarray]] = None, traj_list: List[Dict[Tuple[int, int, int, float], List[ndarray]]] = None, max_length: int = 2):
        if not hasattr(self, '_initialized'):  # 初期化が一度だけ行われるように
            self.traj_data = traj_data if traj_data is not None else {}
            self.traj_list = traj_list if traj_list is not None else []
            self.data_length = 0
            self.max_length = max_length
            self.count = 0
            self._initialized = True

    def assemble(self, current_traj_data: Dict[Tuple[int, int, int, float], List[ndarray]]) -> Dict[Tuple[int, int, int, float], List[ndarray]]:
        self.count += 1
        self.traj_list.append(current_traj_data)

        if len(self.traj_list) > self.max_length:
            self.traj_list.pop(0)

        self._update_traj_data()
        return self.traj_data

    def _update_traj_data(self):
        self.traj_data = {}
        for traj in self.traj_list:
            self.traj_data.update(traj)
