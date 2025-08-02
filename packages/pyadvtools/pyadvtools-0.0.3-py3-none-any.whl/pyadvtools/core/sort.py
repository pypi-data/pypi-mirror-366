import re
from typing import List


def arg_sorted(elements: list, reverse: bool = False) -> List[int]:
    return sorted(range(len(elements)), key=lambda k: elements[k], reverse=reverse)


def sort_strings_with_embedded_numbers(s: str) -> List[str]:
    re_digits = re.compile(r"(\d+)")
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces


def sort_int_str(str_int: List[str], reverse: bool = False) -> List[str]:
    return sorted(str_int, key=sort_strings_with_embedded_numbers, reverse=reverse)


def arg_sort_int_str(str_int: List[str], reverse: bool = False) -> List[int]:
    new_str_int = sort_int_str(str_int, reverse=reverse)
    idx = []
    for i in new_str_int:
        for j in range(len(str_int)):
            if (j not in idx) and (i == str_int[j]):
                idx.append(j)
                break
    return idx


if __name__ == "__main__":
    a = ['abc12.txt','abc9.txt','abc99.txt','abc100.txt','aaa999.txt','234.bat','detail.bat']
    aa = sort_int_str(a)
    print("                :", a)
    print("sorted          :", sorted(a))
    print("arg_sorted      :", arg_sorted(a))
    print("sort_int_str    :", sort_int_str(a))
    print("arg_sort_int_str:", arg_sort_int_str(a))
