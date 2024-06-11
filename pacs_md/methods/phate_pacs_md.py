from pacs_md.methods import BasePaCSMD
from typing import List, Dict
from settings import Settings
import logging
logger = logging.getLogger('pacs_md')

class PHATEPaCSMD(BasePaCSMD):
    def __init__(self):
        self._name = "PHATEPaCS-MD"
        self._description = "PaCS-MD with PHATE"

    def initialize(self, trial: int, initial_file_pathes: List[str], files: List[str], work_dir: str, settings: Settings):
        super().__init__(
            trial=trial,
            initial_file_pathes=initial_file_pathes,
            files=files,
            work_dir=work_dir,
            settings=settings
        )
        logger.info('Initialize {}'.format(self._name))

    def set_mode(self, mode: Dict[str, object]):
        self.set_md(mode['md'])
        self.set_core(mode['evaluater'], mode['analyzer'], mode['selector'])
        self.set_reference_traj()

    def run(self):
        logger.info('Run {}'.format(self._name))
        self.execute()

phate_pacs_md = PHATEPaCSMD()
