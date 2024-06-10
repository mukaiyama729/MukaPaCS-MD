from typing import Dict, Tuple, List, Callable

class BaseResultModel:
    def __init__(self, result: Dict[Tuple, object]={}):
        self._result = result

    def sort_result(self, key: Callable) -> Dict[Tuple, object]:
        return dict(sorted(self.result.items(), key=key))

    def add_result(self, additional_result: Dict[Tuple, object]):
        self._result.update(additional_result)

    def top_result(self, key: Callable, n: int) -> Dict[Tuple, object]:
        return dict(sorted(self.result.items(), key=key)[:n])

    def search(self, key: Tuple[int, int, int, float]) -> object:
        return self.result[key]

    @property
    def result(self) -> Dict[Tuple, object]:
        return self._result
