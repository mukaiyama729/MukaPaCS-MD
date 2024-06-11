import mdtraj as md
from mdtraj import Trajectory, Topology
from typing import Dict, Tuple, List
import numpy as np
from utils import Calculater


class TrajTransformer:
    def __init__(self, traj_objs):
        self.traj_objs: Dict[Tuple[int, int, int], List[Trajectory]] = traj_objs
        self.traj_data: Dict[Tuple[int, int, int, float], List[np.ndarray]] = {}

    def transform(self, align_operator: Dict[Tuple[int, int, int, float], List[np.ndarray]]=dict()):
        for key, trajs in self.traj_objs.items():
            for time, *structures in zip(trajs[0].time, *[traj.xyz for traj in trajs]):
                self.traj_data[key + (time,)] = [structure for structure in structures]

        if any(align_operator):
            self._align_traj(align_operator)

        self._transform_shape()

        return self.traj_data

    def _transform_shape(self):
        for key, structures in self.traj_data.items():
            self.traj_data[key] = [structure.flatten() for structure in structures]

    def _align_traj(self, align_operator: Dict[Tuple[int, int, int, float], List[np.ndarray]]):
        for key, (rotM, transVec) in align_operator.items():
            self.traj_data[key] = [Calculater().alignment(structure, rotM, transVec) for structure in self.traj_data[key]]
