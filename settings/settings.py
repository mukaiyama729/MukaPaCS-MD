import configparser

class Settings:
    file_to_pattern = { 'topol': 'topol*.top', 'index': 'index*.ndx', 'input': 'input*.gro', 'md': 'md*.mdp', 'posres': '*.itp', 'sel': 'sel.dat' }
    patterns = ['*.top', '*.itp', '*.gro', '*.dat', '*.ndx', '*.mdp']

    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.base_dir = self.config['PATH']['base_dir']
        self._set_settings()

    def _set_settings(self):
        self.set_md_settings()
        self.set_pacs_md()
        self.set_core()

    def set_md_settings(self):
        for key, value in self.config['CALCULATE'].items():
            setattr(self, key, value)

    def set_pacs_md(self):
        for key, value in self.config['PaCS-MD'].items():
            setattr(self, key, value)

    def set_core(self):
        self.core = {}
        self.core['analyzer'] = dict(self.config['PHATEANALYZER'].items())
        self.core['evaluater'] = dict(self.config['PHATEEVALUATER'].items())
        self.core['selector'] = dict(self.config['PHATESELECTOR'].items())

