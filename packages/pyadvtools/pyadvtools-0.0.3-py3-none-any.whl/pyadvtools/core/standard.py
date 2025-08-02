import os


def standard_path(p: str) -> str:
    if os.path.basename(p.strip()) == "":
        p = os.path.dirname(p.strip())
    return os.path.expandvars(os.path.expanduser(p.strip()))


if __name__ == "__main__":
    # standard_path
    a = "/Users/test/Documents/"
    b = "/Users/test/Documents"
    print([os.path.basename(a)])  # ['']
    print([os.path.basename(b)])  # ['Documents']
    print([standard_path(a)])  # ['/Users/test/Documents']
    print([standard_path(b)])  # ['/Users/test/Documents']
    print([standard_path("")])  # ['']
    print([standard_path("")])  # ['']
