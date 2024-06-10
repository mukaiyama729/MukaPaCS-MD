from abc import ABC, abstractmethod
import abc
from typing import Dict, Tuple, List


class IMD(metaclass=abc.ABCMeta):

    @abstractmethod
    def single_md(self, total_process: int, threads_per_process: int, use_gpu: bool):
        pass

    @abstractmethod
    def multi_md(self, parallel, multi_dir_pathes: list, total_process: int, threads_per_process: int, use_gpu: bool):
        pass

    @abstractmethod
    def set_input_dir(self, input_dir: str):
        pass

    @abstractmethod
    def set_output_dir(self, output_dir: str):
        pass
