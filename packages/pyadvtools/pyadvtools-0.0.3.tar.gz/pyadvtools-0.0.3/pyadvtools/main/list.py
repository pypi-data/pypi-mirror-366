import re
from typing import List, Union

from pyadvtools.core.check import is_list_contain_list_contain_str, is_list_contain_str


def combine_content_in_list(
    data_list: Union[List[str], List[List[str]]],
    insert_flag: Union[List[str], str, None] = None,
    before_after: str = "after",
) -> List[str]:
    """
    Combine content in list.

    Add insert_flag for every item in data.
    """
    if before_after not in ["after", "before"]:
        before_after = "after"

    if insert_flag is None:
        insert_flag = []
    elif isinstance(insert_flag, str):
        insert_flag = [insert_flag]

    new_list = []
    if is_list_contain_str(data_list):
        for line in data_list:
            if isinstance(line, str):
                if before_after == "after":
                    new_list.append(line)
                    new_list.extend(insert_flag)
                else:
                    new_list.extend(insert_flag)
                    new_list.extend(line)

    elif is_list_contain_list_contain_str(data_list):
        for line in data_list:
            if isinstance(line, list):
                if before_after == "after":
                    new_list.extend(line)
                    new_list.extend(insert_flag)
                else:
                    new_list.extend(insert_flag)
                    new_list.extend(line)
    else:
        pass
    return new_list


def insert_list_in_list(
    data_list: List[str],
    insert_content_list: List[str],
    insert_flag: Union[int, str],
    insert_before_after: str = "after",
    insert_times: float = 1,
) -> List[str]:
    """Insert list in list."""
    new_list = []

    if isinstance(insert_flag, int):
        if insert_flag < len(data_list):
            new_list.extend(data_list[: (insert_flag - 1)])  # the insert_flag in th line
            if insert_before_after == "before":
                new_list.extend(insert_content_list)
                new_list.append(data_list[insert_flag - 1])
            elif insert_before_after == "after":
                new_list.append(data_list[insert_flag - 1])
                new_list.extend(insert_content_list)
            new_list.extend(data_list[insert_flag:])
        else:
            new_list = data_list

    elif isinstance(insert_flag, str):
        cnt = 0
        for line in data_list:
            if cnt < insert_times and re.search(insert_flag, line):
                cnt += 1
                if insert_before_after == "before":
                    new_list.extend(insert_content_list)
                    new_list.append(line)
                elif insert_before_after == "after":
                    new_list.append(line)
                    new_list.extend(insert_content_list)
            else:
                new_list.append(line)
    return new_list


def pairwise_combine_in_list(
    data_list_list_one: List[List[str]], data_list_list_two: List[List[str]], mid_flag: Union[str, list] = "\n"
) -> List[List[str]]:
    """Pair combine."""
    if len(data_list_list_one) == 0:
        return data_list_list_two
    if len(data_list_list_two) == 0:
        return data_list_list_one
    if len(data_list_list_one) != len(data_list_list_two):
        print("The length of the two inputs should be equal.")
        return []

    if isinstance(mid_flag, str):
        mid_flag = [mid_flag]

    new_list_list = []
    for i, j in zip(data_list_list_one, data_list_list_two):
        new_list = []
        new_list.extend(i)
        new_list.extend(j)
        new_list_list.append(new_list)
    return new_list_list


def substitute_in_list(old_list: List[str], new_list: List[str], data_list: List[str]) -> List[str]:
    """Substitute."""
    if len(old_list) != len(new_list):
        print(f"The lengths of {old_list} and {new_list} should be equal.")
        return data_list

    new_data_list = []
    for line in data_list:
        for i, j in zip(old_list, new_list):
            line = re.sub(i, j, line)
        new_data_list.append(line)
    return new_data_list


if __name__ == "__main__":
    pass
