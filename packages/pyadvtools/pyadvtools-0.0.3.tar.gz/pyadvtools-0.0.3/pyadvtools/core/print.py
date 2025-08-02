import time
from functools import wraps


def print_run_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f"Run time for {func.__name__}: {time.time() - start_time}")
        return result

    return wrapper


if __name__ == "__main__":
    pass
