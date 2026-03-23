import os
import hashlib
import threading
import struct
from .base import BaseEngine

class NativeEngine(BaseEngine):
    def __init__(self):
        self._lock = threading.Lock()
        self._reseed()
        if hasattr(os, 'register_at_fork'):
            os.register_at_fork(after_in_child=self._reseed)

    def _reseed(self):
        with self._lock:
            self._entropy = os.urandom(32)
            self._counter = 0

    def random(self):
        with self._lock:
            msg = self._counter.to_bytes(8, 'big')
            ctx = self._entropy + msg
            block = hashlib.sha256(ctx).digest()
            self._counter += 1
            val = int.from_bytes(block[:8], 'big') >> 11
            return val / 9007199254740992.0

    def random_array(self, size):
        if size <= 0:
            return []
        raw_bytes = os.urandom(size * 8)
        ints = struct.unpack(f'{size}Q', raw_bytes)
        return [x / 18446744073709551616.0 for x in ints]