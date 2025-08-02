import os
import shutil
from typing import List


def delete_files(path_storage: str, extensions: List[str]) -> None:
    exts = list(set(extensions))
    for name in os.listdir(path_storage):
        for ext in exts:
            if name.endswith(ext):
                os.remove(os.path.join(path_storage, name))


def delete_empty_lines(data_list: List[str]) -> List[str]:
    return [line for line in data_list if line.strip()]


def delete_empty_lines_first_occur(data_list: List[str]) -> List[str]:
    for i in range(len(data_list)):
        if data_list[i].strip():
            return data_list[i:]
    return []


def delete_empty_lines_last_occur_add_new_line(data_list: List[str]) -> List[str]:
    data_list = delete_empty_lines_first_occur(data_list[::-1])[::-1]
    if data_list:
        data_list[-1] = data_list[-1].rstrip() + "\n"
    return data_list


def delete_python_cache(path_root: str) -> None:
    for root, dirs, _ in os.walk(path_root):
        for folder in dirs:
            if folder == "__pycache__":
                shutil.rmtree(os.path.join(root, folder))


def delete_redundant_elements(element_list: List[str]) -> List[str]:
    new_element_list = [e.strip() for e in element_list if e.strip()]
    return sorted(set(new_element_list), key=new_element_list.index)


if __name__ == "__main__":
    pass
