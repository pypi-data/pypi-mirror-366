from torch._C import DispatchKey


def set_of_dispatch_key():
    return set(DispatchKey.__members__.keys())


def verify_dispatch_key(dispatch_key: str):
    if dispatch_key not in set_of_dispatch_key():
        raise ValueError(f'{dispatch_key} is not valid in dispatch key')
