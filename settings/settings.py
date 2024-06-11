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
        self.use_gpu = self.config['CALCULATE']['use_gpu']
        self.ngpus = self.config['CALCULATE']['ngpus']
        self.process_per_node = self.config['CALCULATE']['process_per_node']
        self.threads_per_process = self.config['CALCULATE']['threads_per_process']
        self.node = self.config['CALCULATE']['node']

    def set_pacs_md(self):
        self.nrounds = self.config['PaCS-MD']['nrounds']
        self.parallel = self.config['PaCS-MD']['parallel']
        self.how_many = self.config['PaCS-MD']['how_many']
        self.nbins = self.config['PaCS-MD']['nbins']
        self.assemble_max_length = self.config['PaCS-MD']['assemble_max_length']
        self.selects = self.config['PaCS-MD']['selects']

    def set_core(self):
        self.core = {}
        self.core['analyzer'] = dict(self.config['PHATEANALYZER'].items())
        self.core['evaluater'] = dict(self.config['PHATEEVALUATER'].items())
        self.core['selector'] = dict(self.config['PHATESELECTOR'].items())

