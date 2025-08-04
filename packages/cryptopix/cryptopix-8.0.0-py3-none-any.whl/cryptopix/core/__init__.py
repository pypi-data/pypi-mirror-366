"""
CryptoPIX Core Module

Contains the core cryptographic implementations of the ChromaCrypt algorithm suite.
"""

from .parameters import (
    ChromaCryptParams,
    CHROMACRYPT_128_PARAMS,
    CHROMACRYPT_192_PARAMS,
    CHROMACRYPT_256_PARAMS,
)

from .lattice import ColorLatticeEngine
from .transforms import ColorTransformEngine
from .chromacrypt_kem import ChromaCryptKEM
from .chromacrypt_sign import ChromaCryptSign
from .color_cipher import ColorCipher
from .color_hash import ColorHash

__all__ = [
    'ChromaCryptParams',
    'CHROMACRYPT_128_PARAMS',
    'CHROMACRYPT_192_PARAMS', 
    'CHROMACRYPT_256_PARAMS',
    'ColorLatticeEngine',
    'ColorTransformEngine',
    'ChromaCryptKEM',
    'ChromaCryptSign',
    'ColorCipher',
    'ColorHash',
]