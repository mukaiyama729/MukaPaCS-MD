import configparser
from typing import List
import os

class Settings:
    file_to_pattern = { 'topol': 'topol*.top', 'index': 'index*.ndx', 'input': 'input*.gro', 'md': 'md*.mdp', 'posres': '*.itp', 'sel': 'sel.dat' }
    patterns = ['*.top', '*.itp', '*.gro', '*.dat', '*.ndx', '*.mdp']

    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.base_dir = self.config['PATH']['base_dir']
        self.core = {}
        self._set_settings()

    def _set_settings(self):
        self.set_md_settings()
        self.set_pacs_md()
        self.set_core()

    def set_logger(self, logging,  level='info',):
        if level == 'info':
            logger = logging.getLogger('pacs_md')
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(os.path.join(self.base_dir, 'pacs_log.log'))
            fmt = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(fmt)
            logger.addHandler(handler)

            selection_logger = logging.getLogger('selection')
            selection_logger.setLevel(logging.INFO)
            handler = logging.FileHandler(os.path.join(self.base_dir, 'selection_log.log'))
            fmt = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(fmt)
            selection_logger.addHandler(handler)

        elif level == 'debug':
            logger = logging.getLogger('pacs_md')
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(os.path.join(self.base_dir, 'pacs_log.log'))
            fmt = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(fmt)
            logger.addHandler(handler)

            selection_logger = logging.getLogger('selection')
            selection_logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(os.path.join(self.base_dir, 'selection_log.log'))
            fmt = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(fmt)
            selection_logger.addHandler(handler)

    def set_md_settings(self):
        self.process_per_node = -1
        self.node = -1
        for key, value in self.config['CALCULATE'].items():
            try:
                setattr(self, key, int(value))
            except ValueError as e:
                print(e)
                setattr(self, key, value)
                continue
            except Exception as e:
                print(e)
                continue
        self.total_processes = self.process_per_node * self.node

    def set_pacs_md(self):
        for key, value in self.config['PACSMD'].items():
            try:
                setattr(self, key, int(value))
            except ValueError as e:
                print(e)
                setattr(self, key, value)
                continue
            except Exception as e:
                print(e)
                continue
        self.selects: List[str] = self.selects.split(',')

    def set_core(self):
        self.core = {}
        self.core['analyzer'] = { key: self.convert_string(value) for key, value in self.config['PHATEANALYZER'].items() }
        self.core['evaluater'] = { key: self.convert_string(value) for key, value in self.config['PHATEEVALUATER'].items() }
        self.core['selector'] = { key: self.convert_string(value) for key, value in self.config['PHATESELECTOR'].items() }
        self.core['visualizer'] = { key: self.convert_string(value) for key, value in self.config['PHATEVISUALIZER'].items() }

    def convert_string(self, s: str):
        # Try to convert to int
        try:
            return int(s)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(s)
        except ValueError:
            pass

        # If not int or float, return as str
        return s

