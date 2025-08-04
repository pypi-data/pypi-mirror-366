"""
Serialization utilities for CryptoPIX keys and data structures.
"""

import json
import base64
import numpy as np
from typing import Dict, Any, Union
from ..core.chromacrypt_kem import ChromaCryptPublicKey, ChromaCryptPrivateKey
from ..core.chromacrypt_sign import ChromaCryptSignatureKey, ChromaCryptSignature

def serialize_key(key: Union[ChromaCryptPublicKey, ChromaCryptPrivateKey, ChromaCryptSignatureKey]) -> str:
    """Serialize a CryptoPIX key to JSON string"""
    if isinstance(key, ChromaCryptPublicKey):
        return _serialize_public_key(key)
    elif isinstance(key, ChromaCryptPrivateKey):
        return _serialize_private_key(key)
    elif isinstance(key, ChromaCryptSignatureKey):
        return _serialize_signature_key(key)
    else:
        raise ValueError("Unsupported key type")

def deserialize_key(data: str, key_type: str) -> Union[ChromaCryptPublicKey, ChromaCryptPrivateKey, ChromaCryptSignatureKey]:
    """Deserialize a CryptoPIX key from JSON string"""
    if key_type == "public":
        return _deserialize_public_key(data)
    elif key_type == "private":
        return _deserialize_private_key(data)
    elif key_type == "signature":
        return _deserialize_signature_key(data)
    else:
        raise ValueError("Unsupported key type")

def serialize_signature(signature: ChromaCryptSignature) -> str:
    """Serialize a ChromaCrypt signature to JSON string"""
    data = {
        'color_commitment': signature.color_commitment,
        'challenge': base64.b64encode(signature.challenge).decode('utf-8'),
        'color_response': _numpy_to_base64(signature.color_response),
        'geometric_proof': signature.geometric_proof,
        'visual_signature': base64.b64encode(signature.visual_signature).decode('utf-8')
    }
    return json.dumps(data)

def _serialize_public_key(key: ChromaCryptPublicKey) -> str:
    """Serialize ChromaCrypt public key"""
    data = {
        'type': 'chromacrypt_public',
        'lattice_matrix': _numpy_to_base64(key.lattice_matrix),
        'color_transform_params': key.color_transform_params,
        'visual_representation': base64.b64encode(key.visual_representation).decode('utf-8'),
        'params': _serialize_params(key.params)
    }
    return json.dumps(data)

def _serialize_private_key(key: ChromaCryptPrivateKey) -> str:
    """Serialize ChromaCrypt private key"""
    data = {
        'type': 'chromacrypt_private',
        'secret_lattice_vector': _numpy_to_base64(key.secret_lattice_vector),
        'color_decode_matrix': _numpy_to_base64(key.color_decode_matrix),
        'geometric_secret': int(key.geometric_secret),
        'params': _serialize_params(key.params)
    }
    return json.dumps(data)

def _serialize_signature_key(key: ChromaCryptSignatureKey) -> str:
    """Serialize ChromaCrypt signature key"""
    data = {
        'type': 'chromacrypt_signature',
        'public_matrix': _numpy_to_base64(key.public_matrix),
        'private_vector': _numpy_to_base64(key.private_vector),
        'color_params': key.color_params,
        'visual_public_key': base64.b64encode(key.visual_public_key).decode('utf-8'),
        'params': _serialize_params(key.params)
    }
    return json.dumps(data)

def _serialize_params(params) -> Dict[str, Any]:
    """Serialize parameter object"""
    return {
        'lattice_dimension': params.lattice_dimension,
        'modulus': params.modulus,
        'error_bound': params.error_bound,
        'color_depth': params.color_depth,
        'geometric_bits': params.geometric_bits,
        'security_level': params.security_level
    }

def _numpy_to_base64(array: np.ndarray) -> str:
    """Convert NumPy array to base64 string"""
    return base64.b64encode(array.tobytes()).decode('utf-8')

def _base64_to_numpy(data: str, dtype=np.int64, shape=None) -> np.ndarray:
    """Convert base64 string back to NumPy array"""
    bytes_data = base64.b64decode(data)
    array = np.frombuffer(bytes_data, dtype=dtype)
    if shape:
        array = array.reshape(shape)
    return array

def _deserialize_public_key(data: str) -> ChromaCryptPublicKey:
    """Deserialize ChromaCrypt public key"""
    # Simplified deserialization for demonstration
    # In production, this would reconstruct the full key object
    raise NotImplementedError("Key deserialization not yet implemented")

def _deserialize_private_key(data: str) -> ChromaCryptPrivateKey:
    """Deserialize ChromaCrypt private key"""
    raise NotImplementedError("Key deserialization not yet implemented")

def _deserialize_signature_key(data: str) -> ChromaCryptSignatureKey:
    """Deserialize ChromaCrypt signature key"""
    raise NotImplementedError("Key deserialization not yet implemented")