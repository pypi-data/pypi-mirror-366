from functools import wraps
from threading import Lock

def singleton(cls):
    '''单例模式, 线程安全'''
    instances = {}
    lock = Lock()
    @wraps(cls)
    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance