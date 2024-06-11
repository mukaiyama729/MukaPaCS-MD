from mdtraj import Trajectory, Topology
import mdtraj as md
import numpy as np
from typing import Dict, Tuple, List
from utils import Calculater


class AlignmentCreater:
    def __init__(self, traj_objs):
        self.traj_objs: Dict[Tuple[int, int, int], Trajectory] = traj_objs
        self.ref_structure: np.ndarray = None
        self.reff_selection: str = None

    def create(self) -> Dict[Tuple[int, int, int, float], Tuple[np.ndarray, np.ndarray]]:
        alignments_operators: Dict[Tuple[int, int, int, float], Tuple[np.ndarray, np.ndarray]] = {}
        for trial, cycle, replica, traj in self.traj_objs.items():

            for time, rotM, transVec in self._alignment(traj):
                alignments_operators[(trial, cycle, replica, time)] = [rotM, transVec]

        # TODO: alignments_operatorsの保存
        return alignments_operators

    def set_ref_structure(self, ref_traj: Trajectory, ref_selection: str='backbone'):
        ref_traj = ref_traj.atom_slice(ref_traj.top.select(ref_selection))
        self.ref_structure = ref_traj.xyz[0]
        self.ref_selection = ref_selection

    def _alignment(self, traj: Trajectory):
        target_traj = traj.atom_slice(traj.top.select(self.ref_selection))
        for time, structure in zip(target_traj.time, target_traj.xyz):
            _, (rotM, transVec) = Calculater().superimpose_coordinates(self.ref_structure, structure)
            yield time, rotM, transVec
