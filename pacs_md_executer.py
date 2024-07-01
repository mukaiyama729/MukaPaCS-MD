import os, shutil, glob
from pacs_md.methods import PHATEPaCSMD, phate_pacs_md
from pacs_md.md import MD
from core.evaluater.phate.phate_evaluater import PHATEEvaluter
from core.analyzer.phate.phate_analyzer import PHATEAnalyzer
from core.selector.phate.phate_selector import PHATESelector
from core.visualizer.phate.phate_visualizer import PHATEVisualizer
import logging
logger = logging.getLogger('pacs_md')

class PaCSMDExecuter:
    def __init__(self, base_dir, settings):
        self.base_dir = base_dir
        self.settings = settings

    def execute_PaCS_MD(self):
        if self.settings.restart:
            instance: PHATEPaCSMD = PHATEPaCSMD.load_instance(self.settings.instance_path)
            instance.rerun()
            if instance.trial >= self.settings.how_many:
                return

            for i in range(instance.trial+1, self.settings.how_may+1, 1):
                dir_path = os.path.join(self.base_dir, 'trial{}'.format(i))
                self.make_dir(dir_path)
                for pattern in self.settings.patterns:
                    self.copy_files(pattern, self.base_dir, dir_path)
                mode = self.create_mode()
                phate_pacs_md.check_necessary_files(dir_path)
                phate_pacs_md.initialize(
                    trial=i,
                    work_dir=dir_path,
                    settings=self.settings
                )
                phate_pacs_md.set_mode(mode)
                phate_pacs_md.run()
        else:
            for i in range(1, self.settings.how_many+1, 1):
                dir_path = os.path.join(self.base_dir, 'trial{}'.format(i))
                self.make_dir(dir_path)
                for pattern in self.settings.patterns:
                    self.copy_files(pattern, self.base_dir, dir_path)
                mode = self.create_mode()

                phate_pacs_md.check_necessary_files(dir_path)
                phate_pacs_md.initialize(
                    trial=i,
                    work_dir=dir_path,
                    settings=self.settings
                )
                phate_pacs_md.set_mode(mode)
                phate_pacs_md.run()

    def create_mode(self):
        if self.settings.mode == 'phate':
            phate_selector = PHATESelector()
            phate_evaluater = PHATEEvaluter()
            phate_visualizer = PHATEVisualizer()
            phate_analyzer = PHATEAnalyzer(selector=phate_selector, evaluator=phate_evaluater)
            mode = {
                'md': MD(),
                'selector': phate_selector,
                'evaluater': phate_evaluater,
                'analyzer': phate_analyzer,
                'visualizer': phate_visualizer,
            }
        logger.info('Mode: {}'.format(mode))
        return mode

    def make_dir(self, dir, exist=True):
        logger.info('Make directory: {}'.format(dir))
        os.makedirs(dir, exist_ok=exist)

    def copy_files(self, pattern, dir1, dir2):
        for file_path in glob.glob(os.path.join(dir1, pattern)):
            logger.info('Copy {} to {}'.format(file_path, dir2))
            shutil.copyfile(file_path, os.path.join(dir2, os.path.basename(file_path)))
