from typing import Dict, Set, List, Tuple
from models.phate import PHATEAnalyzedResultModel
from ..i_visualizer import IVisualizer
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
logger = logging.getLogger('pacs_md')

class PHATEVisualizer(IVisualizer):
    def __init__(self):
        self.path = './'
        self.top_distincts = 30

    def visualize(self) -> None:
        phate_X: np.ndarray = np.array(list(self._analyzed_result.result.values()))

        past_selected_X: np.ndarray = np.array(
                            list(
                                self._past_selected_result(
                                    self._analyzed_result.past_selected_keys,
                                    self._analyzed_result.result
                                ).values()
                            )
                        )

        selected_X: np.ndarray = np.array(
                        list(
                            self._selected_result(
                                self._analyzed_result.distinct_low_central_keys[:self.top_distincts],
                                self._analyzed_result.result
                            ).values()
                        )
                    )

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(1,1,1)
        ax.scatter(phate_X[:,0], phate_X[:,1], color='blue', marker='o', s=0.1, label='original point')

        if np.any(past_selected_X):
            sc = ax.scatter(past_selected_X[:,0], past_selected_X[:,1], c=[i for i in range(past_selected_X.shape[0])], cmap='cool', marker='o', s=40, label='past selected point')
            plt.colorbar(sc)

        ax.scatter(selected_X[:,0], selected_X[:,1], c='black', marker='*', s=50, label='selected point')
        for i in range(selected_X.shape[0]):
            ax.text(selected_X[i, 0], selected_X[i, 1], str(i), fontsize=12, ha='right', va='bottom')

        ax.set_title('phate result cycle{}'.format(self._analyzed_result.current_state[1]))
        ax.set_xlabel('phate1')
        ax.set_ylabel('phate2')
        ax.legend()
        fig.savefig(os.path.join(self.path, 'fig_cyc{}.jpg'.format(self._analyzed_result.current_state[1])))

    def _past_selected_result(self, selected_keys: List[Tuple[int, int, int, float]] | Set, result: Dict[Tuple, np.ndarray]):
        past_selected = {}
        logger.debug('past selected keys: {}'.format(selected_keys))
        if any(selected_keys):
            for key in selected_keys:
                past_selected[key] = result[key]
        return past_selected

    def _selected_result(self, selected_keys: List[Tuple[int, int, int, float]] | Set, result: Dict[Tuple, np.ndarray]):
        past_selected = {}
        logger.info('current selected keys: {}'.format(selected_keys))
        if any(selected_keys):
            for key in selected_keys:
                past_selected[key] = result[key]
        return past_selected

    def set_configuration(self, configuration: Dict[str, object]) -> None:
        self.path = configuration['path'] if configuration['path'] is not None else self.path
        self.top_distincts = configuration['top_distincts'] if configuration['top_distincts'] is not None else None

    def set_analyzed_result_model(self, analyzed_result: PHATEAnalyzedResultModel) -> None:
        self._analyzed_result = analyzed_result

