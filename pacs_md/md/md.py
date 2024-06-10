import os, shutil, re
from command import gmx_command, mpirun_command, mpi_command
from .md import IMD
from typing import List, Dict, Tuple


class MD(IMD):
    def __init__(self, input_dir: str=None, output_dir: str=None):
        self.input_dir = input_dir
        self.output_dir = input_dir if output_dir == None else output_dir

    def single_md(self, total_process: int, threads_per_process: int, use_gpu: bool):
        if use_gpu:
            os.system(self._execute_gpu_command(total_process, threads_per_process))
        else:
            os.system(self._execute_cpu_command(total_process, threads_per_process))

    def _execute_gpu_command(self, total_process: int, threads_per_process: int):
        command = (
            mpirun_command(total_process) +
            'mdrun' +
            ' -s ' + os.path.join(self.input_dir, 'topol.tpr') +
            ' -o ' + os.path.join(self.output_dir, 'traj.trr') +
            ' -x ' + os.path.join(self.output_dir, 'traj_comp.xtc') +
            ' -e ' + os.path.join(self.output_dir, 'ener.edr') +
            ' -g ' + os.path.join(self.output_dir, 'md.log') +
            ' -c ' + os.path.join(self.output_dir, 'confout.gro') +
            ' -cpo ' + os.path.join(self.output_dir, 'state.cpt') +
            ' -pme ' + 'gpu' +
            " -v -ntomp " + str(threads_per_process)
        )
        return command

    def _execute_cpu_command(self, total_process: int, threads_per_process: int):
        command = (
            mpirun_command(total_process) +
            'mdrun' +
            ' -s ' + os.path.join(self.input_dir, 'topol.tpr') +
            ' -o ' + os.path.join(self.output_dir, 'traj.trr') +
            ' -x ' + os.path.join(self.output_dir, 'traj_comp.xtc') +
            ' -e ' + os.path.join(self.output_dir, 'ener.edr') +
            ' -g ' + os.path.join(self.output_dir, 'md.log') +
            ' -c ' + os.path.join(self.output_dir, 'confout.gro') +
            ' -cpo ' + os.path.join(self.output_dir, 'state.cpt') +
            " -v -ntomp " + str(threads_per_process)
        )
        return command

    def multi_md(self, parallel: int, multi_dir_pathes: List[str], total_process: int, threads_per_process: int, use_gpu: bool):
        chunk_size = parallel
        splitted_pathes = [multi_dir_pathes[i:i+chunk_size] for i in range(0, len(multi_dir_pathes), chunk_size)]
        for pathes in splitted_pathes:
            multi_dir = ' '.join(pathes)
            if use_gpu:
                if len(pathes) == parallel:
                    multi_dir = ' '.join(pathes)
                    os.system(self.execute_gpu_multi_command(multi_dir, total_process, threads_per_process))
                else:
                    multi_dir = ' '.join(pathes)
                    process = len(pathes)
                    os.system(self.execute_gpu_multi_command(multi_dir, process, threads_per_process))
            else:
                if len(pathes) == parallel:
                    multi_dir = ' '.join(pathes)
                    os.system(self.execute_cpu_multi_command(multi_dir, total_process, threads_per_process))
                else:
                    multi_dir = ' '.join(pathes)
                    process = len(pathes)
                    os.system(self.execute_cpu_multi_command(multi_dir, total_process, threads_per_process))

    def execute_gpu_multi_command(self, multi_dir_pathes: str, total_process: int, threads_per_process: int):
        command = (
            mpirun_command(total_process) +
            'mdrun' +
            ' -multidir ' + multi_dir_pathes +
            ' -s ' + 'topol' +
            ' -v ' +
            ' -pme ' + 'gpu' +
            ' -npme ' + '1' +
            ' -ntomp ' + str(threads_per_process)
        )
        return command

    def execute_cpu_multi_command(self, multi_dir_pathes: str, total_process: int, threads_per_process: int):
        command = (
            mpirun_command(total_process) +
            'mdrun' +
            ' -multidir ' + multi_dir_pathes +
            ' -s ' + 'topol' +
            ' -v ' +
            ' -ntomp ' + str(threads_per_process)
        )
        return command

    def set_input_dir(self, input_dir: str) -> None:
        self.input_dir = input_dir

    def set_output_dir(self, output_dir: str) -> None:
        self.output_dir = output_dir
