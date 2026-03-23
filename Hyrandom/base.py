import os
import math
import base64
import binascii
import bisect
import itertools

class BaseEngine:
    """Unified API for all Hyrandom engines. Implements standard library interfaces."""
    
    def random(self):
        raise NotImplementedError

    def getrandbits(self, k):
        """Returns a Python integer with k random bits."""
        if k <= 0:
            raise ValueError("number of bits must be greater than zero")
        numbytes = (k + 7) // 8
        x = int.from_bytes(self.token_bytes(numbytes), 'big')
        return x >> (numbytes * 8 - k)

    def getstate(self):
        raise NotImplementedError("Hyrandom acts as a CSPRNG. State extraction is disabled.")

    def setstate(self, state):
        raise NotImplementedError("Hyrandom acts as a CSPRNG. State injection is disabled.")

    def randrange(self, start, stop=None, step=1):
        if stop is None:
            stop, start = start, 0
        width = stop - start
        if step == 1 and width > 0:
            return start + int(self.random() * width)
        raise ValueError("empty range for randrange()")

    def randint(self, a, b):
        return self.randrange(a, b + 1)

    def choice(self, seq):
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
        return seq[int(self.random() * len(seq))]

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        if cum_weights is None:
            if weights is None:
                return [self.choice(population) for _ in range(k)]
            cum_weights = list(itertools.accumulate(weights))
        total = cum_weights[-1]
        return [population[bisect.bisect(cum_weights, self.random() * total)] for _ in range(k)]

    def shuffle(self, x):
        for i in reversed(range(1, len(x))):
            j = int(self.random() * (i + 1))
            x[i], x[j] = x[j], x[i]

    def sample(self, population, k):
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError("Sample larger than population or is negative")
        result = [None] * k
        pool = list(population)
        for i in range(k):
            j = int(self.random() * (n - i))
            result[i] = pool[j]
            pool[j] = pool[n - i - 1]
        return result

    def uniform(self, a, b):
        return a + (b - a) * self.random()

    def triangular(self, low=0.0, high=1.0, mode=None):
        u = self.random()
        c = 0.5 if mode is None else (mode - low) / (high - low)
        if u > c:
            u, c, low, high = 1.0 - u, 1.0 - c, high, low
        return low + (high - low) * math.sqrt(u * c)

    def betavariate(self, alpha, beta):
        y = self.gammavariate(alpha, 1.0)
        if y == 0: return 0.0
        return y / (y + self.gammavariate(beta, 1.0))

    def expovariate(self, lambd):
        return -math.log(1.0 - self.random()) / lambd

    def gammavariate(self, alpha, beta):
        if alpha <= 0.0 or beta <= 0.0:
            raise ValueError("alpha and beta must be > 0.0")
        if alpha > 1.0:
            d = alpha - 1.0 / 3.0
            c = 1.0 / math.sqrt(9.0 * d)
            while True:
                x = self.gauss(0.0, 1.0)
                v = 1.0 + c * x
                if v <= 0.0: continue
                v = v * v * v
                u = self.random()
                if u < 1.0 - 0.0331 * x**4 or math.log(u) < 0.5 * x**2 + d * (1.0 - v + math.log(v)):
                    return d * v * beta
        else:
            u = self.random()
            return self.gammavariate(alpha + 1.0, beta) * math.pow(u, 1.0 / alpha)

    def gauss(self, mu=0.0, sigma=1.0):
        u1, u2 = self.random(), self.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + z * sigma

    def normalvariate(self, mu=0.0, sigma=1.0):
        return self.gauss(mu, sigma)

    def lognormvariate(self, mu, sigma):
        return math.exp(self.gauss(mu, sigma))

    def vonmisesvariate(self, mu, kappa):
        if kappa <= 1e-6:
            return 2.0 * math.pi * self.random()
        a = 1.0 + math.sqrt(1.0 + 4.0 * kappa**2)
        b = (a - math.sqrt(2.0 * a)) / (2.0 * kappa)
        r = (1.0 + b**2) / (2.0 * b)
        while True:
            u1, u2 = self.random(), self.random()
            z = math.cos(math.pi * u1)
            f = (1.0 + r * z) / (r + z)
            c = kappa * (r - f)
            if u2 < c * (2.0 - c) or u2 <= c * math.exp(1.0 - c):
                break
        u3 = self.random()
        return (mu + math.acos(f) * (1.0 if u3 > 0.5 else -1.0)) % (2.0 * math.pi)

    def paretovariate(self, alpha):
        u = 1.0 - self.random()
        return 1.0 / math.pow(u, 1.0 / alpha)

    def weibullvariate(self, alpha, beta):
        u = 1.0 - self.random()
        return alpha * math.pow(-math.log(u), 1.0 / beta)

    def randbelow(self, n):
        if n <= 0:
            raise ValueError("n must be > 0")
        k = n.bit_length()
        while True:
            r = self.getrandbits(k)
            if r < n: return r

    def randbits(self, k):
        return self.getrandbits(k)

    def token_bytes(self, nbytes=32):
        return os.urandom(nbytes)

    def token_hex(self, nbytes=32):
        return binascii.hexlify(self.token_bytes(nbytes)).decode('ascii')

    def token_urlsafe(self, nbytes=32):
        return base64.urlsafe_b64encode(self.token_bytes(nbytes)).decode('ascii').rstrip('=')

    def random_array(self, size):
        """Returns a list of `size` random floats in the range [0.0, 1.0)."""
        if size < 0:
            raise ValueError("Array size must be non-negative")
        return [self.random() for _ in range(size)]

class SystemRandom(BaseEngine):
    """Alias for native OS fallback."""
    def random(self):
        return int.from_bytes(os.urandom(8), 'big') / 18446744073709551616.0
    def random_array(self, size):
        """
        Optimized array generation via entropy batching. 
        Significantly faster than calling random() in a loop.
        """
        raw_bytes = os.urandom(size * 8)
        return [
            int.from_bytes(raw_bytes[i:i+8], 'big') / 18446744073709551616.0 
            for i in range(0, len(raw_bytes), 8)
        ]