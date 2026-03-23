import sys
import time

_engine_instance = None
_current_mode = "None"

def set_engine(mode="auto"):
    """
    Manually override the hyrandom engine.
    Modes: 'auto', 'rust', 'secure', 'fast', 'native'
    """
    global _engine_instance, _current_mode
    
    # 1. Rust Engine (ChaCha20 - Optimized)
    if mode in ("auto", "rust"):
        try:
            from . import _hyrandom_rs
            from .base import BaseEngine
            
            class RustEngine(BaseEngine):
                def random(self): 
                    return _hyrandom_rs.random_float()
                
                def random_array(self, size):
                    if size <= 0: return []
                    return _hyrandom_rs.random_array(size)

                def shuffle(self, x):
                    """
                    Optimized In-place Shuffle.
                    Moves the complexity from Python's interpreter to Rust's native speed.
                    """
                    if not isinstance(x, list):
                        # Fallback for non-list sequences
                        return super().shuffle(x)
                    return _hyrandom_rs.shuffle_list(x)
                
            _engine_instance = RustEngine()
            _current_mode = "Rust (ChaCha20)"
            return
        except ImportError:
            if mode == "rust":
                raise ImportError("Rust extension not found. Please install hyrandom[rust] or use pre-compiled wheels.")

    # 2. NumPy Secure Engine (OS Entropy)
    if mode in ("auto", "secure"):
        try:
            from .numpy_ext import NumpySecureEngine
            _engine_instance = NumpySecureEngine()
            _current_mode = "NumPy (Secure)"
            return
        except ImportError:
            if mode == "secure": raise

    # 3. NumPy Fast Engine (SFC64)
    if mode == "fast":
        try:
            from .numpy_ext import NumpyFastEngine
            _engine_instance = NumpyFastEngine()
            _current_mode = "NumPy (Fast SFC64)"
            return
        except ImportError:
            raise ImportError("NumPy not found. Install via: pip install hyrandom[fast]")

    # 4. Native Fallback (SHA-256)
    from .native import NativeEngine
    _engine_instance = NativeEngine()
    _current_mode = "Native (Hybrid SHA-256)"

# Initialize default optimal engine
set_engine("auto")

# Expose BaseEngine API to module level
def _delegate(name):
    def wrapper(*args, **kwargs):
        return getattr(_engine_instance, name)(*args, **kwargs)
    return wrapper

# Standard API Mapping
random = _delegate("random")
random_array = _delegate("random_array")
getrandbits = _delegate("getrandbits")
getstate = _delegate("getstate")
setstate = _delegate("setstate")
randrange = _delegate("randrange")
randint = _delegate("randint")
choice = _delegate("choice")
choices = _delegate("choices")
shuffle = _delegate("shuffle")
sample = _delegate("sample")
uniform = _delegate("uniform")
triangular = _delegate("triangular")
betavariate = _delegate("betavariate")
expovariate = _delegate("expovariate")
gammavariate = _delegate("gammavariate")
gauss = _delegate("gauss")
normalvariate = _delegate("normalvariate")
lognormvariate = _delegate("lognormvariate")
vonmisesvariate = _delegate("vonmisesvariate")
paretovariate = _delegate("paretovariate")
weibullvariate = _delegate("weibullvariate")
randbelow = _delegate("randbelow")
randbits = _delegate("randbits")
token_bytes = _delegate("token_bytes")
token_hex = _delegate("token_hex")
token_urlsafe = _delegate("token_urlsafe")
SystemRandom = _delegate("SystemRandom")

def get_current_engine():
    """Returns the name of the currently active engine."""
    return _current_mode

def benchmark(iterations=1_000_000):
    """
    Measures the speed of the currently active engine.
    Usage: hyrandom.benchmark()
    """
    print(f"--- hyrandom Benchmark ---")
    print(f"Engine: {_current_mode}")
    print(f"Generating {iterations:,} floats...")
    
    start = time.perf_counter()
    # Use random_array if testing bulk to see true speed
    _engine_instance.random_array(iterations)
    end = time.perf_counter()
    
    duration = end - start
    ops_per_sec = iterations / duration
    print(f"Time elapsed: {duration:.4f} seconds")
    print(f"Operations/sec: {ops_per_sec:,.0f}\n")