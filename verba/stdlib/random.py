import random as _py_random

def random_number(min_val=0, max_val=100):
    val = _py_random.randint(int(min_val), int(max_val))
    return val

def random_choice(lst):
    if not isinstance(lst, list) or not lst:
        return ""
    return _py_random.choice(lst)

def random_shuffle(lst):
    if not isinstance(lst, list):
        return lst
    res = list(lst)
    _py_random.shuffle(res)
    return res

FUNCTIONS = {
    "number": (random_number, ["min", "max"]),
    "choice": (random_choice, ["list"]),
    "shuffle": (random_shuffle, ["list"]),
}
