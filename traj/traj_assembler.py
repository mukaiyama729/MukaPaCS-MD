from mdtraj import Trajectory, Topology
from typing import Dict, Tuple, List
import numpy as np
from numpy import ndarray
from models import MDResultModel


class TrajAssembler:
    def __init__(self, traj_data: Dict[Tuple[int, int, int, float], List[ndarray]]=dict(), traj_list: List[Dict[Tuple[int, int, int, float], List[ndarray]]]=[], max_length: int=2):
        self.traj_data = traj_data
        self.traj_list = traj_list
        self.data_length = 0
        self.max_length = max_length
        self.count = 0

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
