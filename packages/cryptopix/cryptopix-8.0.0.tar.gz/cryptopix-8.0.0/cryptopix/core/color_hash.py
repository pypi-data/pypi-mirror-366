"""
CryptoPIX Color Hash Function

Implements cryptographic hash functions that produce color-based outputs
for unique visual fingerprinting and verification.
"""

import hashlib
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
from io import BytesIO

from .parameters import ChromaCryptParams, get_params
from .transforms import ColorTransformEngine

class ColorHash:
    """Cryptographic hash function with color output"""
    
    def __init__(self, security_level: int = 128, output_size: int = 32):
        """Initialize ColorHash with specified parameters"""
        self.params = get_params(security_level, optimized=False)
        self.color_engine = ColorTransformEngine(self.params)
        self.output_size = output_size  # Number of colors in output
        
    def hash_to_colors(self, data: bytes, 
                      salt: Optional[bytes] = None) -> List[Tuple[int, int, int]]:
        """Hash data to sequence of colors"""
        # Prepare input data
        if salt:
            hash_input = salt + data
        else:
            hash_input = data
        
        # Multi-round hashing for enhanced security
        hash1 = hashlib.sha3_256(hash_input).digest()
        hash2 = hashlib.blake2b(hash_input, digest_size=32).digest()
        hash3 = hashlib.sha256(hash_input).digest()
        
        # Combine hashes
        combined_hash = bytearray()
        for i in range(32):
            combined_hash.append(hash1[i] ^ hash2[i] ^ hash3[i])
        
        # Generate colors from combined hash
        colors = []
        context = {'previous_colors': []}
        
        # Extend hash if needed for more colors
        extended_hash = self._extend_hash(bytes(combined_hash), self.output_size * 3)
        
        for i in range(self.output_size):
            # Extract RGB values
            r = extended_hash[i * 3] if i * 3 < len(extended_hash) else 0
            g = extended_hash[i * 3 + 1] if i * 3 + 1 < len(extended_hash) else 0
            b = extended_hash[i * 3 + 2] if i * 3 + 2 < len(extended_hash) else 0
            
            # Create lattice point
            lattice_point = np.array([r, g, b], dtype=np.int64)
            
            # Apply color transformation with position dependency
            color = self.color_engine.lattice_to_color(
                lattice_point, i, context
            )
            colors.append(color)
            
            # Update context
            context['previous_colors'] = colors[-3:]
        
        return colors
    
    def hash_to_image(self, data: bytes, 
                     salt: Optional[bytes] = None) -> bytes:
        """Hash data to visual image representation"""
        colors = self.hash_to_colors(data, salt)
        
        # Convert colors to bytes representation
        result = bytearray()
        for color in colors:
            result.extend([color[0], color[1], color[2]])
        return bytes(result)
        return self.color_engine.create_visual_representation(colors)
    
    def hash_to_hex_string(self, data: bytes, 
                          salt: Optional[bytes] = None) -> str:
        """Hash data to hex color string"""
        colors = self.hash_to_colors(data, salt)
        return ''.join(f'{r:02x}{g:02x}{b:02x}' for r, g, b in colors)
    
    def verify_hash(self, data: bytes, hash_colors: List[Tuple[int, int, int]], 
                   salt: Optional[bytes] = None) -> bool:
        """Verify data against color hash"""
        computed_colors = self.hash_to_colors(data, salt)
        return computed_colors == hash_colors
    
    def verify_hash_image(self, data: bytes, hash_image: bytes, 
                         salt: Optional[bytes] = None) -> bool:
        """Verify data against hash image"""
        # Extract colors from image
        stored_colors = self.color_engine.extract_colors_from_image(hash_image)
        # Limit to output size to handle padding
        stored_colors = stored_colors[:self.output_size]
        
        # Compute hash
        computed_colors = self.hash_to_colors(data, salt)
        
        return computed_colors == stored_colors
    
    def verify_hash_hex(self, data: bytes, hash_hex: str, 
                       salt: Optional[bytes] = None) -> bool:
        """Verify data against hex color hash"""
        computed_hex = self.hash_to_hex_string(data, salt)
        return computed_hex.lower() == hash_hex.lower()
    
    def create_salted_hash(self, data: bytes) -> Tuple[List[Tuple[int, int, int]], bytes]:
        """Create salted hash with random salt"""
        salt = hashlib.sha256(data + b'salt_gen').digest()[:16]
        colors = self.hash_to_colors(data, salt)
        return colors, salt
    
    def hmac_color_hash(self, data: bytes, key: bytes) -> List[Tuple[int, int, int]]:
        """Create HMAC using color hash"""
        # Standard HMAC construction with color hash
        if len(key) > 64:
            key = hashlib.sha256(key).digest()
        if len(key) < 64:
            key = key + b'\x00' * (64 - len(key))
        
        o_key_pad = bytes(k ^ 0x5C for k in key)
        i_key_pad = bytes(k ^ 0x36 for k in key)
        
        # Inner hash
        inner_data = i_key_pad + data
        inner_colors = self.hash_to_colors(inner_data)
        
        # Convert inner colors back to bytes for outer hash
        inner_bytes = bytearray()
        for r, g, b in inner_colors:
            inner_bytes.extend([r, g, b])
        
        # Outer hash
        outer_data = o_key_pad + bytes(inner_bytes[:32])  # Limit size
        outer_colors = self.hash_to_colors(outer_data)
        
        return outer_colors
    
    def _extend_hash(self, hash_bytes: bytes, target_length: int) -> bytes:
        """Extend hash to target length using deterministic method"""
        if len(hash_bytes) >= target_length:
            return hash_bytes[:target_length]
        
        # Use iterative hashing to extend
        extended = bytearray(hash_bytes)
        counter = 0
        
        while len(extended) < target_length:
            # Hash current content with counter
            next_hash = hashlib.sha256(bytes(extended) + counter.to_bytes(4, 'big')).digest()
            extended.extend(next_hash)
            counter += 1
        
        return bytes(extended[:target_length])
    
    def compare_hashes(self, hash1: List[Tuple[int, int, int]], 
                      hash2: List[Tuple[int, int, int]]) -> float:
        """Compare two color hashes and return similarity score (0.0 to 1.0)"""
        if len(hash1) != len(hash2):
            return 0.0
        
        if not hash1 or not hash2:
            return 1.0 if hash1 == hash2 else 0.0
        
        # Calculate color distance for each position
        total_distance = 0
        max_distance = 0
        
        for (r1, g1, b1), (r2, g2, b2) in zip(hash1, hash2):
            # Euclidean distance in RGB space
            distance = np.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            total_distance += distance
            max_distance += np.sqrt(3 * 255**2)  # Maximum possible distance
        
        # Convert to similarity (1.0 = identical, 0.0 = completely different)
        similarity = 1.0 - (total_distance / max_distance)
        return max(0.0, min(1.0, similarity))
    
    def get_hash_properties(self, colors: List[Tuple[int, int, int]]) -> Dict[str, Any]:
        """Analyze properties of a color hash"""
        if not colors:
            return {'entropy': 0, 'balance': 0, 'distribution': {}}
        
        # Calculate entropy
        color_counts = {}
        for color in colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        total_colors = len(colors)
        entropy = 0
        for count in color_counts.values():
            p = count / total_colors
            if p > 0:
                entropy -= p * np.log2(p)
        
        # Calculate color balance (how evenly distributed RGB values are)
        r_values = [c[0] for c in colors]
        g_values = [c[1] for c in colors]
        b_values = [c[2] for c in colors]
        
        r_std = np.std(r_values) if r_values else 0
        g_std = np.std(g_values) if g_values else 0
        b_std = np.std(b_values) if b_values else 0
        
        balance = (r_std + g_std + b_std) / 3
        
        # Color distribution analysis
        distribution = {
            'unique_colors': len(color_counts),
            'most_common': max(color_counts.values()) if color_counts else 0,
            'avg_r': np.mean(r_values) if r_values else 0,
            'avg_g': np.mean(g_values) if g_values else 0,
            'avg_b': np.mean(b_values) if b_values else 0,
        }
        
        return {
            'entropy': entropy,
            'balance': balance,
            'distribution': distribution,
            'total_colors': total_colors,
            'unique_colors': len(color_counts)
        }
    
    def benchmark_hash(self, data_size: int = 1024, iterations: int = 100) -> Dict[str, float]:
        """Benchmark hash performance"""
        import time
        
        # Generate test data
        test_data = b'A' * data_size
        
        # Benchmark color hash
        start_time = time.time()
        for _ in range(iterations):
            self.hash_to_colors(test_data)
        color_time = time.time() - start_time
        
        # Benchmark standard SHA256 for comparison
        start_time = time.time()
        for _ in range(iterations):
            hashlib.sha256(test_data).digest()
        sha256_time = time.time() - start_time
        
        return {
            'color_hash_time': color_time,
            'sha256_time': sha256_time,
            'color_hash_per_second': iterations / color_time if color_time > 0 else 0,
            'sha256_per_second': iterations / sha256_time if sha256_time > 0 else 0,
            'relative_performance': sha256_time / color_time if color_time > 0 else 0
        }