from typing import List, Dict, Tuple
import numpy as np
from mdtraj import Trajectory, Topology
import mdtraj as md

class TrajManipulater:

    def __init__(self, traj_objs: Dict[Tuple[int, int, int], Trajectory]):
        self.traj_obj = traj_objs

    def add_traj(self, traj_objs: Dict[Tuple[int, int, int], Trajectory]):
        self.traj_obj.update(traj_objs)

    def delete_traj(self, condition: Tuple[int, int, int]):
        keys_to_remove = [key for key in self.traj_obj.keys() if condition]
        for key in keys_to_remove:
            del self.traj_obj[key]

    def sort_traj(self):
        return dict(sorted(self.traj_obj.items(), key=lambda x: x[0]))
