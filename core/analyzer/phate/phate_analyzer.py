from typing import Dict, List, Tuple, Set
from ..i_analyzer import IAnalyzer
from models import MDResultModel, AnalyzedResultModel
from models.phate import PHATEAnalyzedResultModel
from core.selector.i_selector import ISelector
from core.evaluater.i_evaluater import IEvaluater
import phate
import numpy as np
import logging
from scipy.sparse.linalg import eigs
logger = logging.getLogger('pacs_md')

class PHATEAnalyzer(IAnalyzer):
    def __init__(self, selector: ISelector, evaluator: IEvaluater):
        self.md_result: MDResultModel = None
        self.phate_operator = None
        self.use_past_trajectory = False
        self.use_selected_structures = True
        self.alpha_decay = 5
        self.knn = 5
        self.n_components = 2
        self.num_powered_iterations = 200
        self.max_centrals = 100
        self.authority = False
        self.analyzed_result: np.ndarray = None # (data num, 2 dim)
        self.use_distinct_indices: bool = False
        self.use_approximation: bool = True
        self.which: str = 'LM'
        self.how_many_eigs: int = 200
        self.distinct_low_centrals: List[int] = []

        self.selector: ISelector = selector
        self.evaluator: IEvaluater = evaluator

    def analyze(self) -> PHATEAnalyzedResultModel:
        self.phate_operator = phate.PHATE(n_components=self.n_components, knn=self.knn, decay=self.alpha_decay)
        current_state = self.md_result.current_state

        analyzed_data, past_selected_keys, past_selected_structures = self._create_data_for_analysis()
        analyzed_data_keys = list(analyzed_data.keys())
        past_selected_indices = [i for i in range(len(past_selected_keys))]
        logger.info('past selected indices: {}'.format(past_selected_indices))
        logger.debug('analyzed_data: {}'.format(list(analyzed_data.keys())))

        #複数のList[np.ndarray]を一つのnp.ndarrayに変換
        traj = np.array(list(analyzed_data.values())).reshape(len(analyzed_data), -1)

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
            logger.info('pre distinct centrals: {}'.format(self.distinct_low_centrals))
        else:
            eigen_values = None
            eigen_vectors = None
            top_low_centrals = sorted_centrals[:self.max_centrals]
            self.distinct_low_centrals = top_low_centrals
            logger.info('pre distinct centrals: {}'.format(self.distinct_low_centrals))

        if self.use_selected_structures:
            logger.info('use selected structures')
            self.distinct_low_centrals = self._exclude_past_points(self.distinct_low_centrals, past_selected_indices)

        distinct_low_central_keys = [analyzed_data_keys[i] for i in self.distinct_low_centrals]
        logger.info('distinct low central keys: {}'.format(distinct_low_central_keys))

        logger.info('distinct low centrals: {},'.format(self.distinct_low_centrals))
        phate_analyzed_result_model = self._create_analyzed_result_model(
            analyzed_data,
            current_state,
            original_data=analyzed_data,
            index_to_key=dict(zip([i for i in range(len(analyzed_data))], analyzed_data.keys())),
            max_centrals=self.max_centrals,
            eigen_centrals=eigen_centrals,
            sorted_centrals=sorted_centrals,
            eigen_values=eigen_values,
            eigen_vectors=eigen_vectors,
            top_low_centrals=top_low_centrals,
            distinct_indices=distinct_indices,
            distinct_low_centrals=self.distinct_low_centrals,
            distinct_low_central_keys=[analyzed_data_keys[i] for i in self.distinct_low_centrals],
            past_selected_keys=past_selected_keys,
            past_selected_structures=past_selected_structures,
            past_selected_indices=past_selected_indices
        )

        return phate_analyzed_result_model

    def _exclude_past_points(self, distinct_low_centrals: List[int], past_selected_indices: List[int]):
        if any(past_selected_indices):
            logger.debug('past selected indices: {}'.format(past_selected_indices))
            distinct_low_centrals = np.array(distinct_low_centrals)
            scores = []
            for i in past_selected_indices:
                scores.append(np.sqrt(np.linalg.norm(np.array((self.phate_operator.diff_potential[distinct_low_centrals,:] - self.phate_operator.diff_potential[i,:])), axis=1, ord=2)))

            scores = np.array(scores)
            weights = np.linspace(10, 1, scores.shape[0])
            scores = np.average(scores, axis=0, weights=weights)
            logger.info('scores: {}'.format(scores))
            best_points = list(np.argsort(scores))[::-1]
            return list(distinct_low_centrals[best_points])
        return distinct_low_centrals

    def _create_data_for_analysis(self) -> Tuple[Dict[Tuple[int, int, int, float], List[np.ndarray]], Set[Tuple[int, int, int, float]] | Set]:
        past_selected_structures = dict()
        past_selected_keys = []
        if not self.use_past_trajectory:
            result: Dict[Tuple[int, int, int, float], List[np.ndarray]]  = self.md_result.get_current_result()
        else:
            result: Dict[Tuple[int, int, int, float], List[np.ndarray]] = self.md_result.result
        logger.debug('result: {}'.format(result.keys()))
        if self.use_selected_structures:
            past_selected_structures = self.selector.past_selected_structures()
            logger.info('past selected structures: {}'.format(past_selected_structures.keys()))
            past_selected_keys = list(past_selected_structures.keys())
            logger.debug('past selected keys: {}'.format(past_selected_keys))
        return { **past_selected_structures, **result }, past_selected_keys, past_selected_structures

    def _create_analyzed_result_model(self, used_md_results: Dict[Tuple[int, int, int, float], List[np.ndarray]], current_state,  **kwargs):
        analyzed_results = {}

        for key, result in zip(used_md_results.keys(), self.analyzed_result):
            analyzed_results[key] = result

        return PHATEAnalyzedResultModel(analyzed_results, current_state).from_map(kwargs)

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
        v = np.ones(n)

        for i in range(self.num_powered_iterations):
            v_next = r**(-1) * (A_temp @ v)
            v_next = v_next / np.sum(v_next)
            v_next = np.array(v_next).flatten()

            if np.linalg.norm(v_next - v) < self.tol:
                logger.info(f'Converged in {i+1} iterations')
                return v_next

            v = v_next.flatten()

        logger.info('Reached maximum iterations without full convergence')
        return v

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
        self.tol = configuration['tol'] if configuration['tol'] is not None else self.tol
        self.max_centrals = configuration['max_centrals'] if configuration['max_centrals'] is not None else self.max_centrals
        self.use_distinct_indices = configuration['use_distinct_indices'] if configuration['use_distinct_indices'] is not None else self.use_distinct_indices
        self.use_approximation = configuration['use_approximation'] if configuration['use_approximation'] is not None else self.use_approximation
        self.which = configuration['which'] if configuration['which'] is not None else self.which
        self.how_many_eigs = configuration['how_many_eigs'] if configuration['how_many_eigs'] is not None else self.how_many_eigs
        self.use_past_trajectory = bool(configuration['use_past_trajectory']) if configuration['use_past_trajectory'] is not None else bool(self.use_past_trajectory)
        self.use_selected_structures = bool(configuration['use_selected_structures']) if configuration['use_selected_structures'] is not None else bool(self.use_selected_structures)
