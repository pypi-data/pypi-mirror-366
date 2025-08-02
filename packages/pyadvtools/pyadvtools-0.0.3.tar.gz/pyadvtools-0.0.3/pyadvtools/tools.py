import os
import re
from typing import List, Union

from pyadvtools.core.sort import sort_int_str
from pyadvtools.core.standard import standard_path
from pyadvtools.main.dict import IterateSortDict, IterateUpdateDict
from pyadvtools.main.list import combine_content_in_list
from pyadvtools.main.read_write import read_list


def iterate_obtain_full_file_names(
    path_storage: str,
    extension: str,
    reverse: bool = True,
    is_standard_file_name: bool = True,
    search_year_list: List[str] = [],
) -> List[str]:
    """Iterate obtain full file names."""
    if not os.path.exists(path_storage):
        return []

    regex = None
    if is_standard_file_name and search_year_list:
        regex = re.compile(f'({"|".join(search_year_list)})')

    file_list = []
    for root, _, files in os.walk(path_storage, topdown=True):
        files = [f for f in files if f.endswith(f".{extension}".replace("..", "."))]

        if regex:
            files = [f for f in files if regex.search(f)]

        file_list.extend([os.path.join(root, f) for f in files])

    file_list = sort_int_str(file_list, reverse=reverse)
    return file_list


def transform_to_data_list(
    original_data: Union[List[str], str],
    extension: str,
    reverse: bool = False,
    is_standard_file_name: bool = True,
    search_year_list: List[str] = [],
    insert_flag: Union[List[str], str, None] = None,
    before_after: str = "after"
) -> List[str]:
    """Transform from file, str, list[str] to list[str]."""
    if isinstance(original_data, str):
        if os.path.isdir(original_data):
            files = iterate_obtain_full_file_names(
                standard_path(original_data), extension, reverse, is_standard_file_name, search_year_list
            )
            data_list = combine_content_in_list([read_list(f, "r", None) for f in files], insert_flag, before_after)
        elif original_data.strip().endswith(extension) or os.path.isfile(original_data):
            data_list = read_list(original_data, "r", None)
        else:
            data_list = original_data.splitlines(keepends=True)
    else:
        data_list = original_data
    return data_list


def generate_nested_dict(path_storage: str) -> dict:
    files_dict = {}
    for root, _, files in os.walk(path_storage, topdown=True):
        for file in files:
            f = "." + os.path.join(root, file).replace(path_storage, "")
            files_dict.setdefault(root.replace(path_storage, ""), []).append(f)

    files_dict = {k: sorted(v) for k, v in files_dict.items()}

    nested_dict = {}
    for k, v in files_dict.items():
        keys = [i for i in k.split("/") if i.strip()]

        if not keys:
            continue

        temp_dict = {keys[-1]: v}
        for j in keys[::-1][1:]:
            temp_dict = {j: temp_dict}

        nested_dict = IterateUpdateDict().dict_update(nested_dict, temp_dict)

    nested_dict = IterateSortDict().dict_update(nested_dict)
    return nested_dict
