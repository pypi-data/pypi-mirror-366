"""
Validation utilities for CryptoPIX parameters and data structures.
"""

from typing import Tuple, List, Union, Any

def validate_security_level(security_level: int) -> bool:
    """Validate security level parameter"""
    valid_levels = [128, 192, 256]
    return security_level in valid_levels

def validate_color_format(color: Tuple[int, int, int]) -> bool:
    """Validate RGB color tuple format"""
    if not isinstance(color, (tuple, list)) or len(color) != 3:
        return False
    
    return all(isinstance(c, int) and 0 <= c <= 255 for c in color)

def validate_color_sequence(colors: List[Tuple[int, int, int]]) -> bool:
    """Validate a sequence of colors"""
    if not isinstance(colors, list) or len(colors) == 0:
        return False
    
    return all(validate_color_format(color) for color in colors)

def validate_key_parameters(params: Any) -> bool:
    """Validate key parameter structure"""
    required_attrs = ['lattice_dimension', 'modulus', 'error_bound', 'security_level']
    
    for attr in required_attrs:
        if not hasattr(params, attr):
            return False
        
        value = getattr(params, attr)
        if not isinstance(value, int) or value <= 0:
            return False
    
    return True

def validate_message_format(message: bytes) -> bool:
    """Validate message format for signing/encryption"""
    return isinstance(message, bytes) and len(message) > 0

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password strength and return issues"""
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password should contain uppercase letters")
    
    if not any(c.islower() for c in password):
        issues.append("Password should contain lowercase letters")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password should contain numbers")
    
    return len(issues) == 0, issues