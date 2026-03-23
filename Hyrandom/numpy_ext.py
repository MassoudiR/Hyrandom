import os
from .base import BaseEngine

try:
    import numpy as np
except ImportError:
    np = None

class NumpySecureEngine(BaseEngine):
    def __init__(self):
        if np is None:
            raise ImportError("NumPy is required. Run: pip install hyrandom[secure]")
        self._m32 = 2.3283064365386963e-10

    def random(self):
        return int.from_bytes(os.urandom(4), 'big') * self._m32

    def random_array(self, size):
        if size <= 0:
            return []
        raw_bytes = os.urandom(size * 4)
        arr = np.frombuffer(raw_bytes, dtype=np.uint32)
        return (arr * self._m32).tolist()

class NumpyFastEngine(BaseEngine):
    def __init__(self):
        if np is None:
            raise ImportError("NumPy is required. Run: pip install hyrandom[fast]")
        self._rng = np.random.Generator(np.random.SFC64())

    def random(self):
        return float(self._rng.random())

    def random_array(self, size):
        if size <= 0:
            return []
        return self._rng.random(size).tolist()