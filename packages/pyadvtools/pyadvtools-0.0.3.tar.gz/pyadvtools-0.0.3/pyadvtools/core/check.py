from typing import Any, List


def is_empty(x: Any) -> bool:
    """Check whether the input is empty.

    "" is str type and the length is 0.
    "".isspace() = False
    " ".isspace() = True
    len({}) == 0
    len([]) == 0
    len(()) == 0
    len("") == 0
    """
    if (isinstance(x, str) and (len(x.strip()) == 0)) or (len(x) == 0) or (x is None) or (x is False):
        return True
    return False


def is_list_contain_str(xx: List[Any]) -> bool:
    """List[str]."""
    return all([isinstance(x, str) for x in xx])


def is_list_contain_list_contain_str(xxx: List[Any]) -> bool:
    """[list[List[str]]]."""
    return all([is_list_contain_str(xx) for xx in xxx])


if __name__ == "__main__":
    pass

