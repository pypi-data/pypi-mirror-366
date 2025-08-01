
from pyphg._pyphg import *

import inspect

from pyphg import _pyphg as _C

__all__ = []
__name, __obj="", None
for __name in dir(_C):
    __all__.append(__name)
    if callable(__obj) or inspect.isclass(__obj):
        if __obj.__module__ != __name__:
            __obj.__module__ = __name__

del __name, __obj
