import os, shutil, glob
from pacs_md import phate_pacs_md
from pacs_md.md import MD
from core.evaluater.phate.phate_evaluater import PHATEEvaluter
from core.analyzer.phate.phate_analyzer import PHATEAnalyzer
from core.selector.phate.phate_selector import PHATESelector

class PaCSMDExecuter:

    def __init__(self, base_dir, settings):
        self.base_dir = base_dir
        self.settings = settings

    def execute_PaCS_MD(self):
        for i in range(1, self.settings.how_many+1, 1):
            dir_path = os.path.join(self.base_dir, 'trial{}'.format(i))
            self.make_dir(dir_path)
            for pattern in self.settings.patterns:
                self.copy_files(pattern, self.base_dir, dir_path)
            mode = self.create_mode()
            phate_pacs_md.initialize(
                trial=i,
                initial_file_pathes=self.settings.initial_file_pathes,
                files=self.settings.files,
                work_dir=dir_path,
                settings=self.settings
            )
            phate_pacs_md.set_mode(mode)
            phate_pacs_md.run()

    def create_mode(self):
        if self.settings.mode == 'phate':
            mode = {
                'md': MD(),
                'evaluater': PHATEEvaluter(),
                'analyzer': PHATEAnalyzer(),
                'selector': PHATESelector(),
            }
        return mode

    def make_dir(self, dir, exist=True):
        os.makedirs(dir, exist_ok=exist)

    def copy_files(self, pattern, dir1, dir2):
        for file_path in glob.glob(os.path.join(dir1, pattern)):
            shutil.copyfile(file_path, os.path.join(dir2, os.path.basename(file_path)))
