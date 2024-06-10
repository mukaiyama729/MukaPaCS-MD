import mdtraj as md
from mdtraj import Trajectory, Topology
from typing import Dict, Tuple, List
import numpy as np

class TrajSelector:
    def __init__(self, traj_obj: Dict[Tuple[int, int, int], Trajectory]):
        self.traj_obj = traj_obj
        self._selects: List[str] = []
        self.traj_objs: Dict[Tuple[int, int, int], List[Trajectory]] = {}

    def set_selects(self, selects: List[str]) -> None:
        self._selects = selects

    def select(self) -> Dict[Tuple[int, int, int], List[Trajectory]]:

        for key, traj in self.traj_obj.items():
            self.traj_objs[key] = self._select(traj)

        return self.traj_objs

    def _select(self, traj) -> List[Trajectory]:
        return [traj.atom_slice(traj.top.select(select)) for select in self._selects]
