"""
CryptoPIX - Revolutionary Post-Quantum Cryptographic Library

This library implements the world's first Color Lattice Learning with Errors (CLWE)
cryptographic system, providing unprecedented post-quantum security through innovative
color transformation techniques.

Copyright (c) 2025 CryptoPIX Team
License: MIT
"""

__version__ = "6.0.0"
__author__ = "CryptoPIX Team"
__email__ = "founder@cryptopix.in"
__license__ = "MIT"

# Core cryptographic primitives
from .core.chromacrypt_kem import ChromaCryptKEM
from .core.chromacrypt_sign import ChromaCryptSign
from .core.color_cipher import ColorCipher
from .core.color_hash import ColorHash

# Utility classes and functions
from .core.lattice import ColorLatticeEngine
from .core.transforms import ColorTransformEngine
from .core.parameters import (
    ChromaCryptParams,
    CHROMACRYPT_128_PARAMS,
    CHROMACRYPT_192_PARAMS,
    CHROMACRYPT_256_PARAMS,
)

# Utility imports
from .utils.performance import PerformanceProfiler, enable_optimizations
from .utils.validation import validate_security_level, validate_color_format
from .utils.serialization import serialize_key, deserialize_key

# Convenience functions
def create_kem(security_level: int = 128) -> ChromaCryptKEM:
    """Create ChromaCrypt KEM instance with specified security level"""
    return ChromaCryptKEM(security_level)

def create_signature_scheme(security_level: int = 128) -> ChromaCryptSign:
    """Create ChromaCrypt signature scheme instance with specified security level"""
    return ChromaCryptSign(security_level)

def create_cipher(security_level: int = 128, fast_mode: bool = False) -> ColorCipher:
    """Create ColorCipher instance with specified security level"""
    cipher = ColorCipher(security_level)
    cipher.fast_mode = fast_mode
    return cipher

def create_hash(security_level: int = 128) -> ColorHash:
    """Create ColorHash instance with specified security level"""
    return ColorHash(security_level)

# Version information
def get_version_info():
    """Get detailed version information"""
    return {
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'algorithms': ['ChromaCrypt-KEM', 'ChromaCrypt-Sign', 'ColorCipher', 'ColorHash'],
        'security_levels': [128, 192, 256],
        'post_quantum': True
    }

# Export all public APIs
__all__ = [
    # Core classes
    'ChromaCryptKEM',
    'ChromaCryptSign', 
    'ColorCipher',
    'ColorHash',
    
    # Engine classes
    'ColorLatticeEngine',
    'ColorTransformEngine',
    
    # Parameters
    'ChromaCryptParams',
    'CHROMACRYPT_128_PARAMS',
    'CHROMACRYPT_192_PARAMS', 
    'CHROMACRYPT_256_PARAMS',
    
    # Convenience functions
    'create_kem',
    'create_signature_scheme',
    'create_cipher',
    'create_hash',
    'get_version_info',
    
    # Legacy compatibility
    'encrypt_text_to_image_v2',
    'decrypt_image_to_text_v2',
    
    # Version info
    '__version__',
    '__author__',
    '__license__',
]

# Initialize logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Print welcome message for interactive use
import sys
if hasattr(sys, 'ps1'):  # Interactive mode
    print(f"CryptoPIX v{__version__} - Revolutionary Post-Quantum Cryptography")
    print("Try: cryptopix.create_kem() or cryptopix.create_signature_scheme()")