import copy
from typing import Any, Dict, List

from pyadvtools.core.sort import sort_int_str


class IterateSortDict(object):
    def __init__(self, reverse: bool = False) -> None:
        self.reverse = reverse

    def dict_update(self, old):
        """Update."""
        old = self.dict_sort_iteration(old)
        old = self.dict_sort(old)
        return old

    def dict_sort_iteration(self, old: dict):
        """Sort."""
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    def dict_sort(self, old: dict):
        """Sort."""
        return {k: old[k] for k in sort_int_str(list(old.keys()), self.reverse)}


class IterateUpdateDict(object):
    def __init__(self) -> None:
        pass

    def dict_update(self, old: dict, new: dict) -> dict:
        """Update."""
        old = self.dict_update_iteration(old, new)
        old = self.dict_add(old, new)
        return old

    def dict_update_iteration(self, old: dict, new: dict) -> dict:
        """Update."""
        for key in old:
            if key not in new:
                continue

            if isinstance(old[key], dict) and isinstance(new[key], dict):
                old[key] = self.dict_update(old[key], new[key])
            else:
                old[key] = new[key]  # update

        return old

    @staticmethod
    def dict_add(old: dict, new: dict) -> dict:
        """Add."""
        for key in new:
            if key not in old:
                old[key] = new[key]
        return old


class IterateCombineExtendDict(object):
    """Combine iterately and the deepest layer has the form: Dict[str, List[Any]]."""

    def __init__(self) -> None:
        pass

    def dict_update(self, data_dict: Dict[str, Any]) -> List[Any]:
        """Update."""
        data_dict = self.dict_update_iteration(copy.deepcopy(data_dict))
        data_list = self.data_combine(data_dict)
        return data_list

    def dict_update_iteration(self, old: Dict[str, Any]) -> Dict[str, Any]:
        """Update."""
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    @staticmethod
    def data_combine(old: Dict[str, Any]) -> List[Any]:
        """Add."""
        data_list = []
        for key in old:
            data_list.extend(old[key])
        return data_list


if __name__ == "__main__":
    a = {"a": {"e": {"d": ["dd"]}, "c": ["cc"]}, "b": ["bb"]}
    aa = IterateCombineExtendDict().dict_update(a)
    print(aa)  # ['dd', 'cc', 'bb']

    b = IterateSortDict().dict_update(a)
    print(b)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'b': ['bb']}

    c = {'aa': ['111'], 'b': ['222']}
    cc = IterateUpdateDict().dict_update(a, c)
    print(cc)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'b': ['222'], 'aa': ['111']}

    d = IterateSortDict().dict_update(cc)
    print(d)  # {'a': {'c': ['cc'], 'e': {'d': ['dd']}}, 'aa': ['111'], 'b': ['222']}
