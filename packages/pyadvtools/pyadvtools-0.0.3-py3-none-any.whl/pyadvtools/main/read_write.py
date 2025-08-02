import os
import re
from typing import List, Optional, Union

from pyadvtools.core.delete import delete_empty_lines_first_occur, delete_empty_lines_last_occur_add_new_line


def is_valid_filename(filename):
    if not filename:
        return False

    if any(char in filename for char in '<>:"/\\|?*'):
        return False

    if filename.startswith('.') and (not filename[1:]):
        return False

    if '..' in filename:
        return False

    if filename[0] == ' ' or filename[-1] == ' ':
        return False

    if '  ' in filename:
        return False

    if '.' not in filename:
        return False

    return True


def read_list(file_name: str, read_flag: str = "r", path_storage: Optional[str] = None) -> List[str]:
    """Read."""
    if path_storage is not None:
        file_name = os.path.join(path_storage, file_name)

    if (not os.path.isfile(file_name)) or (not os.path.exists(file_name)):
        return []

    with open(file_name, read_flag) as f:
        data_list = f.readlines()
    return delete_empty_lines_last_occur_add_new_line(data_list)


def write_list(
    data_list: Union[List[str], List[bytes]],
    file_name: str,
    write_flag: str = "w",
    path_storage: Optional[str] = None,
    check: bool = True,
    delete_first_empty: bool = True,
    delete_last_empty: bool = True,
    compulsory: bool = False,
    delete_original_file: bool = False,
) -> None:
    """Write."""
    if not is_valid_filename(name := os.path.basename(file_name)):
        print(f"Invalid file name: {name}")
        return None

    if path_storage is None:
        full_file_name = file_name
    else:
        full_file_name = os.path.join(path_storage, file_name)

    full_path = os.path.dirname(full_file_name)

    if all([isinstance(i, bytes) for i in data_list]) and (write_flag == "wb"):
        if (full_path != "") and (not os.path.exists(full_path)):
            os.makedirs(full_path)

        temp_data_list = [i for i in data_list if isinstance(i, bytes)]
        with open(full_file_name, "wb") as f:
            f.writelines(temp_data_list)

    else:
        if not all([isinstance(i, str) for i in data_list]):
            return None

        new_data_list = [i for i in data_list if isinstance(i, str)]
        if delete_last_empty:
            new_data_list = delete_empty_lines_last_occur_add_new_line(new_data_list)
        if delete_first_empty:
            new_data_list = delete_empty_lines_first_occur(new_data_list)

        if new_data_list or compulsory:
            if (full_path != "") and (not os.path.exists(full_path)):
                os.makedirs(full_path)

            if (not re.search("a", write_flag)) and check and os.path.isfile(full_file_name):
                print(f"{full_file_name} has existed and do nothing.")
            else:
                with open(full_file_name, write_flag) as f:
                    f.writelines(new_data_list)

        elif delete_original_file:
            if os.path.exists(full_file_name):
                os.remove(full_file_name)
    return None


if __name__ == "__main__":
    print(is_valid_filename("test.md"))  # True
    print(is_valid_filename("test"))  # False
