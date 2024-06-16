from typing import Dict, List, Tuple
from ..i_analyzer import IAnalyzer
from models import MDResultModel, AnalyzedResultModel
from models.phate import PHATEAnalyzedResultModel
import phate
import numpy as np
import logging
from scipy.sparse.linalg import eigs
logger = logging.getLogger('pacs_md')

class PHATEAnalyzer(IAnalyzer):
    def __init__(self):
        self.md_result = None
        self.phate_operator = None
        self.use_past_trajectory = False
        self.alpha_decay = 5
        self.knn = 5
        self.n_components = 2
        self.num_powered_iterations = 40
        self.max_centrals = 50
        self.authority = False
        self.analyzed_result = None
        self.use_distinct_indices = False
        self.use_approximation = True
        self.which = 'LM'
        self.how_many_eigs = 100

    def analyze(self) -> PHATEAnalyzedResultModel:
        self.phate_operator = phate.PHATE(n_components=self.n_components, knn=self.knn, decay=self.alpha_decay)
        current_state = self.md_result.current_state
        if not self.use_past_trajectory:
            result = self.md_result.get_current_result()
        else:
            result = self.md_result.result()
        logger.info('result: {}'.format(result))

        #複数のList[np.ndarray]を一つのnp.ndarrayに変換
        traj = np.array(list(result.values())).reshape(len(result), -1)

        traj_data = np.array(traj).astype(np.float64)
        self.analyzed_result = self.phate_operator.fit_transform(traj_data)

        eigen_centrals = np.asarray(self.cal_eigenvector_centrality())
        sorted_centrals = list(np.argsort(eigen_centrals).flatten())
        logger.info('sorted centrals: {}'.format(sorted_centrals))

        distinct_indices = []
        if self.use_distinct_indices:
            eigen_values, eigen_vectors = self.cal_eigenvectors()

            for eigen_vec in eigen_vectors.T[:]:
                distinct_indices.append(np.argsort(eigen_vec)[-1])
                distinct_indices.append(np.argsort(eigen_vec)[0])

            distinct_indices = list(set(distinct_indices))
            top_low_centrals = sorted_centrals[:self.max_centrals]
            logger.info('distinct indices: {}'.format(distinct_indices))
            logger.info('top low centrals: {}'.format(top_low_centrals))
            logger.info('sorted centrals: {}'.format(sorted_centrals))
            self.distinct_low_centrals = self._create_distinct_low_centrals(distinct_indices, sorted_centrals)
        else:
            eigen_values = None
            eigen_vectors = None
            top_low_centrals = sorted_centrals[:self.max_centrals]
            self.distinct_low_centrals = top_low_centrals

        logger.info('distinct low centrals: {},'.format(self.distinct_low_centrals))
        phate_analyzed_result_model = self.create_analyzed_result_model(
            result,
            current_state,
            max_centrals=self.max_centrals,
            eigen_centrals=eigen_centrals,
            sorted_centrals=sorted_centrals,
            eigen_values=eigen_values,
            eigen_vectors=eigen_vectors,
            top_low_centrals=top_low_centrals,
            distinct_indices=distinct_indices,
            distinct_low_centrals=self.distinct_low_centrals
        )

        return phate_analyzed_result_model

    def create_analyzed_result_model(self, used_md_results: Dict[Tuple[int, int, int, float], List[np.ndarray]], current_state,  **kwargs):
        analyzed_result = {}

        for key, result in zip(used_md_results.keys(), self.analyzed_result):
            analyzed_result[key] = result

        return PHATEAnalyzedResultModel(analyzed_result, current_state).from_map(kwargs)

    def cal_eigenvector_centrality(self):
        def spectral_radius(M):
            """
            Compute the spectral radius of M.
            """
            if self.use_approximation:
                try:
                    eigenvalue, _ = eigs(A_temp, k=1, which='LM')
                    max_abs_eigenvalue = np.abs(eigenvalue[0])
                    return max_abs_eigenvalue
                except Exception as e:
                    print(e)
                    logger.info('Error has happened: {}'.format(e))
                    return np.max(np.abs(np.linalg.eigvals(M)))
            return np.max(np.abs(np.linalg.eigvals(M)))

        affinity_matrix = self.phate_operator.graph.diff_aff.todense()
        A_temp = affinity_matrix.T if self.authority else affinity_matrix
        n = len(A_temp)
        r = spectral_radius(A_temp)
        e = r**(-self.num_powered_iterations) * (np.linalg.matrix_power(A_temp, self.num_powered_iterations) @ np.ones(n))
        return e / np.sum(e)

    def cal_eigenvectors(self) -> Tuple[np.ndarray, np.ndarray]:
        diff_op = np.asarray(self.phate_operator.graph.diff_op.todense())
        # TODO: kの値を変更する
        eigen_values, eigen_vectors = eigs(diff_op, k=self.how_many_eigs, which=self.which)
        return eigen_values, eigen_vectors

    def _create_distinct_low_centrals(self, distinct_indices: List[int], sorted_centrals: List[int]) -> List[int]:
        length = len(distinct_indices)
        distinct_low_centrals = []
        i = 0
        while True:
            partial_low_centrals = sorted_centrals[:self.max_centrals + i]
            distinct_low_centrals = list(set(partial_low_centrals) & set(distinct_indices))
            if (len(distinct_low_centrals) >= self.max_centrals or len(distinct_low_centrals) >= length):
                logger.info('i: {}'.format(i))
                break
            i += 1
        return distinct_low_centrals

    def set_md_result(self, md_result: MDResultModel) -> None:
        self.md_result = md_result

    def set_configuration(self, configuration: Dict[str, object]) -> None:
        self.num_cycles = configuration['num_cycles'] if configuration['num_cycles'] is not None else self.num_cycles
        self.alpha_decay = configuration['alpha_decay'] if configuration['alpha_decay'] is not None else self.alpha_decay
        self.knn = configuration['knn'] if configuration['knn'] is not None else self.knn
        self.n_components = configuration['n_components'] if configuration['n_components'] is not None else self.n_components
        self.num_powered_iterations = configuration['num_powered_iterations'] if configuration['num_powered_iterations'] is not None else self.num_powered_iterations
        self.max_centrals = configuration['max_centrals'] if configuration['max_centrals'] is not None else self.max_centrals
        self.use_distinct_indices = configuration['use_distinct_indices'] if configuration['use_distinct_indices'] is not None else self.use_distinct_indices
        self.use_approximation = configuration['use_approximation'] if configuration['use_approximation'] is not None else self.use_approximation
        self.which = configuration['which'] if configuration['which'] is not None else self.which
        self.how_many_eigs = configuration['how_many_eigs'] if configuration['how_many_eigs'] is not None else self.how_many_eigs
        self.use_past_trajectory = bool(configuration['use_past_trajectory']) if configuration['use_past_trajectory'] is not None else bool(self.use_past_trajectory)
