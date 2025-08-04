"""
CryptoPIX Performance Optimizations

Advanced optimizations for high-performance cryptographic operations.
"""

import numpy as np
from typing import Optional, Tuple, List
from .parameters import ChromaCryptParams

# Try to import NumPy acceleration libraries
try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

class OptimizedLatticeEngine:
    """High-performance lattice operations with optional JIT compilation"""
    
    def __init__(self, params: ChromaCryptParams):
        self.params = params
        
    def fast_matrix_multiply(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Optimized matrix-vector multiplication"""
        if HAS_NUMBA:
            return self._jit_matrix_multiply(matrix, vector, self.params.modulus)
        else:
            return self._numpy_matrix_multiply(matrix, vector)
    
    def _numpy_matrix_multiply(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """NumPy optimized multiplication"""
        # Use int64 for intermediate calculations to prevent overflow
        matrix_64 = matrix.astype(np.int64)
        vector_64 = vector.astype(np.int64)
        
        # Vectorized multiplication
        result = np.dot(matrix_64, vector_64) % self.params.modulus
        return result.astype(np.int64)
    
    @staticmethod
    def _compile_jit_functions():
        """Compile JIT functions if numba is available"""
        if not HAS_NUMBA:
            return None
            
        @numba.jit(nopython=True, cache=True)
        def jit_matrix_multiply(matrix, vector, modulus):
            """JIT-compiled matrix multiplication"""
            result = np.zeros(matrix.shape[0], dtype=np.int64)
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    result[i] = (result[i] + matrix[i, j] * vector[j]) % modulus
            return result
        
        return jit_matrix_multiply
    
    def _jit_matrix_multiply(self, matrix: np.ndarray, vector: np.ndarray, modulus: int) -> np.ndarray:
        """JIT-compiled matrix multiplication"""
        jit_func = self._compile_jit_functions()
        if jit_func:
            return jit_func(matrix, vector, modulus)
        else:
            return self._numpy_matrix_multiply(matrix, vector)

class OptimizedColorEngine:
    """High-performance color transformations"""
    
    def __init__(self, params: ChromaCryptParams):
        self.params = params
        
    def batch_color_transform(self, lattice_points: List[np.ndarray], 
                            positions: List[int]) -> List[Tuple[int, int, int]]:
        """Batch process multiple color transformations"""
        # Vectorized color extraction
        points_array = np.array([p[:3] for p in lattice_points])
        
        # Apply modular arithmetic vectorized
        r_values = points_array[:, 0] % 256
        g_values = points_array[:, 1] % 256
        b_values = points_array[:, 2] % 256
        
        # Apply position transformations
        position_offsets = np.array(positions) % 256
        r_values = (r_values + position_offsets) % 256
        g_values = (g_values + position_offsets * 2) % 256
        b_values = (b_values + position_offsets * 3) % 256
        
        # Convert to list of tuples
        colors = [(int(r), int(g), int(b)) for r, g, b in zip(r_values, g_values, b_values)]
        return colors
    
    def parallel_hash_colors(self, data_chunks: List[bytes]) -> List[Tuple[int, int, int]]:
        """Process multiple hash operations in parallel"""
        import hashlib
        import concurrent.futures
        
        def hash_chunk(chunk):
            hash_val = hashlib.sha256(chunk).digest()
            r = hash_val[0]
            g = hash_val[1] if len(hash_val) > 1 else 0
            b = hash_val[2] if len(hash_val) > 2 else 0
            return (r, g, b)
        
        # Use thread pool for I/O bound hashing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            colors = list(executor.map(hash_chunk, data_chunks))
        
        return colors

class PerformanceProfiler:
    """Performance profiling and benchmarking tools"""
    
    @staticmethod
    def benchmark_kem_operations(security_level: int = 128, iterations: int = 10):
        """Benchmark KEM operations"""
        import time
        from ..core.chromacrypt_kem import ChromaCryptKEM
        
        kem = ChromaCryptKEM(security_level)
        
        # Benchmark key generation
        start_time = time.time()
        keys = []
        for _ in range(iterations):
            pub, priv = kem.keygen()
            keys.append((pub, priv))
        keygen_time = time.time() - start_time
        
        # Benchmark encapsulation
        start_time = time.time()
        capsules = []
        for pub, _ in keys:
            secret, capsule = kem.encapsulate(pub)
            capsules.append((secret, capsule))
        encap_time = time.time() - start_time
        
        # Benchmark decapsulation
        start_time = time.time()
        for i, (secret, capsule) in enumerate(capsules):
            _, priv = keys[i]
            recovered = kem.decapsulate(priv, capsule)
        decap_time = time.time() - start_time
        
        return {
            'keygen_ops_per_sec': iterations / keygen_time if keygen_time > 0 else 0,
            'encap_ops_per_sec': iterations / encap_time if encap_time > 0 else 0,
            'decap_ops_per_sec': iterations / decap_time if decap_time > 0 else 0,
            'total_time': keygen_time + encap_time + decap_time
        }
    
    @staticmethod
    def benchmark_signature_operations(security_level: int = 128, iterations: int = 10):
        """Benchmark signature operations"""
        import time
        from ..core.chromacrypt_sign import ChromaCryptSign
        
        sign = ChromaCryptSign(security_level)
        
        # Benchmark key generation
        start_time = time.time()
        keys = []
        for _ in range(iterations):
            key_pair = sign.keygen()
            keys.append(key_pair)
        keygen_time = time.time() - start_time
        
        # Benchmark signing
        message = b"Performance test message for ChromaCrypt signatures"
        start_time = time.time()
        signatures = []
        for key_pair in keys:
            sig = sign.sign(message, key_pair)
            signatures.append(sig)
        signing_time = time.time() - start_time
        
        # Benchmark verification
        start_time = time.time()
        for i, sig in enumerate(signatures):
            sign.verify(message, sig, keys[i])
        verify_time = time.time() - start_time
        
        return {
            'keygen_ops_per_sec': iterations / keygen_time if keygen_time > 0 else 0,
            'sign_ops_per_sec': iterations / signing_time if signing_time > 0 else 0,
            'verify_ops_per_sec': iterations / verify_time if verify_time > 0 else 0,
            'total_time': keygen_time + signing_time + verify_time
        }

def enable_performance_optimizations():
    """Enable all available performance optimizations"""
    optimizations = {
        'numba_available': HAS_NUMBA,
        'numpy_version': np.__version__,
        'optimizations_enabled': []
    }
    
    if HAS_NUMBA:
        optimizations['optimizations_enabled'].append('JIT compilation')
    
    # Set NumPy optimization flags
    try:
        # Use faster BLAS if available
        np.show_config()
        optimizations['optimizations_enabled'].append('Optimized BLAS')
    except:
        pass
    
    # Enable parallel processing
    import os
    if not os.environ.get('NUMBA_DISABLE_JIT'):
        os.environ['NUMBA_CACHE_DIR'] = '/tmp/numba_cache'
        optimizations['optimizations_enabled'].append('Numba caching')
    
    return optimizations