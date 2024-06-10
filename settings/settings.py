

class Settings:
    file_to_pattern = { 'topol': 'topol*.top', 'index': 'index*.ndx', 'input': 'input*.gro', 'md': 'md*.mdp', 'posres': '*.itp', 'sel': 'sel.dat' }
    patterns = ['*.top', '*.itp', '*.gro', '*.dat', '*.ndx', '*.mdp']

    @classmethod
    def set_phate_MD(cls, nbins, nround, parallel, target, how_many=1, file_name='delaunay_data', threshold=0.1, threads_per_process=1, process_per_node=1, use_gpu=True, node=1):
        cls.nround = nround
        cls.parallel = parallel
        cls.how_many = how_many
        cls.nbins = nbins
        cls.target = target
        cls.file_name = file_name
        cls.threshold = threshold
        cls.threads_per_process = threads_per_process
        cls.process_per_node = process_per_node
        cls.use_gpu = use_gpu
        cls.node = node
        cls.total_processes = cls.process_per_node * cls.node
