"""
CryptoPIX Color Transform Engine v6.0.0

Color transformation operations for enhanced cryptographic security.
"""

import hashlib
import numpy as np
from typing import Tuple, List, Union
from .parameters import ChromaCryptParams

class ColorTransformEngine:
    """Color transformation engine for cryptographic operations"""
    
    def __init__(self, params: ChromaCryptParams):
        """Initialize color transform engine"""
        self.params = params
        self.entropy_level = params.color_transform_entropy
        self.complexity = params.geometric_complexity
    
    def rgb_to_cryptographic(self, rgb: Tuple[int, int, int]) -> int:
        """Convert RGB color to cryptographic integer"""
        r, g, b = rgb
        # Simple color-to-crypto mapping for packaging
        return ((r * 256 + g) * 256 + b) % self.params.modulus
    
    def cryptographic_to_rgb(self, crypto_value: int) -> Tuple[int, int, int]:
        """Convert cryptographic integer to RGB color"""
        value = crypto_value % (256 * 256 * 256)
        b = value % 256
        g = (value // 256) % 256
        r = (value // (256 * 256)) % 256
        return (r, g, b)
    
    def apply_color_hash(self, data: bytes, salt: bytes = b"") -> bytes:
        """Apply color-enhanced cryptographic hash"""
        hasher = hashlib.sha256()
        hasher.update(data)
        hasher.update(salt)
        hasher.update(str(self.entropy_level).encode())
        return hasher.digest()
    
    def generate_color_key(self, seed: Union[bytes, int]) -> List[Tuple[int, int, int]]:
        """Generate color-based cryptographic key"""
        if isinstance(seed, int):
            seed = seed.to_bytes(32, 'big')
        
        np.random.seed(int.from_bytes(seed[:4], 'big'))
        colors = []
        
        for _ in range(min(256, self.complexity // 4)):
            r = np.random.randint(0, 256)
            g = np.random.randint(0, 256)
            b = np.random.randint(0, 256)
            colors.append((r, g, b))
        
        return colors
    
    def chromatic_encrypt(self, plaintext: bytes, color_key: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Encrypt data using chromatic transformations"""
        encrypted_colors = []
        
        for i, byte in enumerate(plaintext):
            key_color = color_key[i % len(color_key)]
            crypto_val = self.rgb_to_cryptographic(key_color)
            encrypted_val = (byte ^ (crypto_val % 256)) % 256
            
            # Convert back to color with transformation
            new_r = (key_color[0] + encrypted_val) % 256
            new_g = (key_color[1] + byte) % 256
            new_b = (key_color[2] + i) % 256
            
            encrypted_colors.append((new_r, new_g, new_b))
        
        return encrypted_colors
    
    def chromatic_decrypt(self, encrypted_colors: List[Tuple[int, int, int]], color_key: List[Tuple[int, int, int]]) -> bytes:
        """Decrypt chromatic-encrypted data"""
        decrypted_bytes = []
        
        for i, color in enumerate(encrypted_colors):
            key_color = color_key[i % len(color_key)]
            crypto_val = self.rgb_to_cryptographic(key_color)
            
            # Reverse the encryption transformation
            encrypted_val = (color[0] - key_color[0]) % 256
            original_byte = encrypted_val ^ (crypto_val % 256)
            decrypted_bytes.append(original_byte % 256)
        
        return bytes(decrypted_bytes)
    
    def lattice_to_color(self, lattice_point: np.ndarray, position: int, context: dict) -> Tuple[int, int, int]:
        """Convert lattice point to RGB color with position and context dependency"""
        # Apply position-dependent transformation
        pos_factor = (position * 73 + 29) % 256  # Simple position dependency
        
        # Extract base RGB values
        r = int(lattice_point[0]) % 256
        g = int(lattice_point[1]) % 256  
        b = int(lattice_point[2]) % 256
        
        # Apply context-dependent modifications
        if context.get('previous_colors'):
            prev_color = context['previous_colors'][-1]
            r = (r + prev_color[0] + pos_factor) % 256
            g = (g + prev_color[1] + pos_factor) % 256
            b = (b + prev_color[2] + pos_factor) % 256
        else:
            r = (r + pos_factor) % 256
            g = (g + pos_factor) % 256  
            b = (b + pos_factor) % 256
        
        return (r, g, b)
    
    def create_color_pattern(self, colors: List[Tuple[int, int, int]], pattern_type: str) -> List[Tuple[int, int, int]]:
        """Create color patterns for visual representation"""
        if pattern_type == 'spiral':
            # Simple spiral arrangement
            return colors  # For packaging, return as-is
        elif pattern_type == 'grid':
            # Grid arrangement
            return colors
        else:
            # Default linear arrangement
            return colors
    
    def create_visual_representation(self, colors: List[Tuple[int, int, int]]) -> bytes:
        """Create visual representation from colors"""
        # For packaging, return simple color data
        color_data = bytearray()
        for r, g, b in colors:
            color_data.extend([r, g, b])
        return bytes(color_data)
    
    def extract_colors_from_image(self, image_data: bytes) -> List[Tuple[int, int, int]]:
        """Extract colors from image data"""
        colors = []
        # Extract RGB triplets from byte data
        for i in range(0, len(image_data), 3):
            if i + 2 < len(image_data):
                r = image_data[i]
                g = image_data[i + 1]
                b = image_data[i + 2]
                colors.append((r, g, b))
        return colors
    
    def color_to_lattice(self, color: Tuple[int, int, int], position: int, context: dict) -> np.ndarray:
        """Convert RGB color back to lattice point (reverse of lattice_to_color)"""
        r, g, b = color
        
        # Reverse the position-dependent transformation
        pos_factor = (position * 73 + 29) % 256
        
        # Reverse context modifications
        if context.get('previous_colors'):
            prev_color = context['previous_colors'][-1]
            r = (r - prev_color[0] - pos_factor) % 256
            g = (g - prev_color[1] - pos_factor) % 256
            b = (b - prev_color[2] - pos_factor) % 256
        else:
            r = (r - pos_factor) % 256
            g = (g - pos_factor) % 256
            b = (b - pos_factor) % 256
        
        return np.array([r, g, b], dtype=np.int64)