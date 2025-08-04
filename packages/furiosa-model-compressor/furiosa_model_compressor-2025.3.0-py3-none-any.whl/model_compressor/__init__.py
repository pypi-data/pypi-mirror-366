"""model_compressor draft release"""
from .api import *

def get_version(module):
    try:
        import pkgutil

        return str(pkgutil.get_data(module, 'VERSION.txt'), encoding="UTF-8")
    except:
        pass

    try:
        from importlib.metadata import version

        return version(module)
    except:
        pass

    return "N/A"


__version__ = get_version(__package__)
