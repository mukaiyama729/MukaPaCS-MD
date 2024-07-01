from .base_pacs_md import BasePaCSMD
from typing import List, Dict
from settings import Settings
import logging
import glob, shutil, os
import pickle
logger = logging.getLogger('pacs_md')


class PHATEPaCSMD(BasePaCSMD):
    def __init__(self):
        self._name = "PHATEPaCS-MD"
        self._description = "PaCS-MD with PHATE"

    def initialize(self, trial: int, work_dir: str, settings: Settings):
        super().__init__(
            trial=trial,
            initial_file_pathes=self.file_pathes,
            files=self.files,
            work_dir=work_dir,
            settings=settings
        )
        logger.info('Initialize {}'.format(self._name))

    def set_mode(self, mode: Dict[str, object]):
        self.set_md(mode['md'])
        self.set_core(mode['evaluater'], mode['analyzer'], mode['selector'], mode['visualizer'])
        self.set_reference_traj()

    def check_necessary_files(self, work_dir) -> None:
        self.file_pathes = {}
        self.files = {}
        for file_name, pattern in Settings.file_to_pattern.items():
            self._check_file(file_name, pattern, work_dir)

    def _check_file(self, file_name: str, pattern: str, work_dir: str) -> None:
        files = glob.glob(os.path.join(work_dir, pattern))
        if file_name == 'posres':
            self.file_pathes[file_name] = files
            self.files[file_name] = []
            if not(files):
                pass
            else:
                for file_path in files:
                    self.files[file_name].append(os.path.basename(file_path))
        else:
            if any(files) and len(files) == 1:
                self.file_pathes[file_name] = files[0]
                self.files[file_name] = os.path.basename(files[0])
            elif any(files) and len(files) > 1:
                self.file_pathes = files[0]
                self.files = os.path.basename(files[0])
            else:
                raise FileNotFoundError('File not found: {}'.format(file_name))

    def run(self):
        logger.info('Run {}'.format(self._name))
        try:
            self.execute()
        except Exception as e:
            logger.error(e)
            self.save_instance()
        self.save_instance()


    def rerun(self):
        logger.info('Run {}'.format(self._name))
        try:
            self.restart()
        except Exception as e:
            logger.error(e)
            self.save_instance()
        self.save_instance()


    def save_instance(self) -> None:
        logger.info('Save instance')
        logger.info('Save instance to {}'.format(self.work_dir))
        with open(os.path.join(self.work_dir, 'instance-trial-{}.pickle'.format(self.trial)), 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load_instance(cls, instance_path: str) -> "cls":
        with open(instance_path, 'rb') as f:
            return pickle.load(f)

phate_pacs_md = PHATEPaCSMD()
