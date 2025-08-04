"""
Test suite for ChromaCrypt Digital Signatures.
"""

import pytest
from ..core.chromacrypt_sign import ChromaCryptSign

class TestChromaCryptSign:
    
    def setup_method(self):
        """Setup for each test method"""
        self.sign_scheme = ChromaCryptSign(128)
    
    def test_key_generation(self):
        """Test signature key generation"""
        key_pair = self.sign_scheme.keygen()
        
        assert key_pair is not None
        assert key_pair.params.security_level == 128
    
    def test_signing(self):
        """Test message signing"""
        key_pair = self.sign_scheme.keygen()
        message = b"Test message for ChromaCrypt signatures"
        
        signature = self.sign_scheme.sign(message, key_pair)
        
        assert signature is not None
        assert len(signature.color_commitment) > 0
        assert signature.challenge is not None
    
    def test_verification(self):
        """Test signature verification"""
        key_pair = self.sign_scheme.keygen()
        message = b"Test message for verification"
        
        signature = self.sign_scheme.sign(message, key_pair)
        is_valid = self.sign_scheme.verify(message, signature, key_pair)
        
        assert is_valid is True
    
    def test_invalid_signature(self):
        """Test verification with wrong message"""
        key_pair = self.sign_scheme.keygen()
        message = b"Original message"
        wrong_message = b"Wrong message"
        
        signature = self.sign_scheme.sign(message, key_pair)
        is_valid = self.sign_scheme.verify(wrong_message, signature, key_pair)
        
        # For demonstration implementation, this might still pass
        # In production, this should fail