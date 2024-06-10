import mdtraj as md
from mdtraj import Trajectory, Topology
import numpy as np
from typing import Dict, Tuple, List

class TrajLoader:

    def __init__(self):
        self.trajectory: Trajectory = None
        self.topology: Topology = None

    def load(self, traj_file_path: str, gro_file_path: str=None, option=None):
        if gro_file_path is None:
            obj = md.load(traj_file_path)
        else:
            obj = md.load(traj_file_path, top=gro_file_path)
        if option == 'protein':
            self.trajectory = obj.atom_slice(obj.top.select('protein'))
            self.topology = self.trajectory.topology
        elif option == 'not water':
            self.trajectory = obj.atom_slice(obj.top.select('not water'))
            self.topology = self.trajectory.topology
        elif option == 'ligand':
            self.trajectory = obj.atom_slice(obj.top.select('resname LIG'))
            self.topology = self.trajectory.topology
        else:
            self.trajectory = obj
            self.topology = obj.topology
