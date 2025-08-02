import re
from typing import List, Union


def convert_to_ordered_number(number: int) -> Union[str, int]:
    if number < 0:
        return number

    new_number = number % 100
    number_list_1 = (1, 21, 31, 41, 51, 61, 71, 81, 91)
    number_list_2 = (2, 22, 32, 42, 52, 62, 72, 82, 92)
    number_list_3 = (3, 23, 33, 43, 53, 63, 73, 83, 93)

    if new_number in number_list_1:
        return f"{number}st"
    elif new_number in number_list_2:
        return f"{number}nd"
    elif new_number in number_list_3:
        return f"{number}rd"
    return f"{number}rd"


def months_list() -> List[str]:
    month_contents_old, month_contents_new = [], []

    m1 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    m2 = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    m3 = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    m4 = ["jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]  # May
    m4_1 = ["sept"]
    m5 = ["spring", "summer", "fall", "winter", "quarter"]

    for months in [m1, m2, m3, m4, m4_1]:
        month_contents_old.extend(months)

    for i in month_contents_old:
        for j in month_contents_old:
            if i != j:
                month_contents_new.extend([f"{i}-{j}", f"{i}/{j}"])

    month_contents = []

    month_contents.extend(month_contents_old)
    month_contents.extend(month_contents_new)

    month_contents.extend(m5)

    for i in m5:
        for j in m5:
            if i != j:
                month_contents.extend([f"{i}-{j}", f"{i}/{j}"])

    return month_contents


def months_dict(str_int: str = "str"):
    months = {
        'January': ['1', 1],
        'February': ['2', 2],
        'March': ['3', 3],
        'April': ['4', 4],
        'May': ['5', 5],
        'June': ['6', 6],
        'July': ['7', 7],
        'August': ['8', 8],
        'September': ['9', 9],
        'October': ['10', 10],
        'November': ['11', 11],
        'December': ['12', 12],
        'Jan': ['1', 1],
        'Feb': ['2', 2],
        'Mar': ['3', 3],
        'Apr': ['4', 4],
        'Jun': ['6', 6],
        'Jul': ['7', 7],
        'Aug': ['8', 8],
        'Sep': ['9', 9],
        'Sept': ['9', 9],
        'Oct': ['10', 10],
        'Nov': ['11', 11],
        'Dec': ['12', 12],
        '01': ['1', 1],
        '02': ['2', 2],
        '03': ['3', 3],
        '04': ['4', 4],
        '05': ['5', 5],
        '06': ['6', 6],
        '07': ['7', 7],
        '08': ['8', 8],
        '09': ['9', 9],
        '1': ['1', 1],
        '2': ['2', 2],
        '3': ['3', 3],
        '4': ['4', 4],
        '5': ['5', 5],
        '6': ['6', 6],
        '7': ['7', 7],
        '8': ['8', 8],
        '9': ['9', 9],
        '10': ['10', 10],
        '11': ['11', 11],
        '12': ['12', 12],
    }
    if str_int == "str":
        return {key.strip().lower(): months[key][0] for key in months}
    elif str_int == "int":
        return {key.strip().lower(): months[key][1] for key in months}
    else:
        return {}


def convert_str_month_to_number_month(month: str) -> str:
    months = months_dict("str")

    month = month.strip()
    if month == "":
        return month

    new_month = month

    month_ = re.sub(r"[–\-/]+", "-", month.strip().lower()).replace(".", "")
    if month_ in months_list():
        if months.get(month_):
            new_month = months.get(month_, month)
            new_month = new_month.title()
        else:
            new_months = [months.get(i.strip().lower(), i) for i in month_.split("-")]
            new_months = [m.title() for m in new_months]
            new_month = "-".join(new_months)
    else:
        print(f"Not standard month: `{month}` in `convert_str_month_to_number_month`.")
    return new_month


if __name__ == "__main__":
    print(months_list())
    print(len(months_list()))
