from .pacs_md import PaCSMD
from typing import List, Dict

class PHATEPaCSMD(PaCSMD):
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

    def set_mode(self, mode: Dict[str, object]):
        self.set_md(mode['md'])
        self.set_core(mode['evaluater'], mode['analyzer'], mode['selector'])
        self.set_reference_traj()

    def run(self):
        self.execute()

phate_pacs_md = PHATEPaCSMD()
