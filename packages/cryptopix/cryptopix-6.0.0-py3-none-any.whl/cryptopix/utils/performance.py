"""
Performance utilities and optimization tools for CryptoPIX.
"""

import time
import statistics
from typing import Dict, List, Any, Callable
import numpy as np

# Optional imports for performance
try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

class PerformanceProfiler:
    """Performance profiling and benchmarking utilities"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, func: Callable, *args, iterations: int = 100, **kwargs) -> Dict[str, float]:
        """Benchmark a function with multiple iterations"""
        times = []
        
        for _ in range(iterations):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            times.append(end - start)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std': statistics.stdev(times) if len(times) > 1 else 0,
            'ops_per_sec': iterations / sum(times) if sum(times) > 0 else 0
        }
    
    def profile_kem_operations(self, kem_instance, iterations: int = 50):
        """Profile KEM operations"""
        # Key generation
        keygen_stats = self.benchmark_function(
            kem_instance.keygen, iterations=iterations
        )
        
        # Generate a key pair for encap/decap tests
        pub_key, priv_key = kem_instance.keygen()
        
        # Encapsulation
        encap_stats = self.benchmark_function(
            kem_instance.encapsulate, pub_key, iterations=iterations
        )
        
        # Decapsulation (simplified for benchmark)
        secret, capsule = kem_instance.encapsulate(pub_key)
        decap_stats = self.benchmark_function(
            kem_instance.decapsulate, priv_key, capsule, iterations=iterations
        )
        
        return {
            'keygen': keygen_stats,
            'encapsulate': encap_stats,
            'decapsulate': decap_stats
        }

def enable_optimizations() -> Dict[str, Any]:
    """Enable all available performance optimizations"""
    optimizations = {
        'numba_available': HAS_NUMBA,
        'numpy_version': np.__version__,
        'enabled_optimizations': []
    }
    
    if HAS_NUMBA:
        optimizations['enabled_optimizations'].append('JIT compilation')
    
    # Set NumPy threading
    try:
        import os
        os.environ['MKL_NUM_THREADS'] = '4'
        os.environ['NUMEXPR_NUM_THREADS'] = '4'
        optimizations['enabled_optimizations'].append('Multi-threading')
    except:
        pass
    
    return optimizations

def optimize_matrix_operations():
    """Optimize matrix operations for better performance"""
    if HAS_NUMBA:
        @numba.jit(nopython=True, cache=True)
        def fast_matrix_multiply(a, b, mod):
            result = np.zeros((a.shape[0], b.shape[1]), dtype=np.int64)
            for i in range(a.shape[0]):
                for j in range(b.shape[1]):
                    for k in range(a.shape[1]):
                        result[i, j] = (result[i, j] + a[i, k] * b[k, j]) % mod
            return result
        return fast_matrix_multiply
    else:
        def numpy_matrix_multiply(a, b, mod):
            return np.dot(a, b) % mod
        return numpy_matrix_multiply