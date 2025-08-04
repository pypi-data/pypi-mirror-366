from .core import _routes

def site(path):
    def decorator(func):
        _routes[path] = func
        return func
    return decorator

def start():
    def decorator(func):
        return func
    return decorator
