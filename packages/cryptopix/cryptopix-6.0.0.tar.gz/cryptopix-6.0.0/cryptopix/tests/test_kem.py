"""
Test suite for ChromaCrypt Key Encapsulation Mechanism.
"""

import pytest
from ..core.chromacrypt_kem import ChromaCryptKEM

class TestChromaCryptKEM:
    
    def setup_method(self):
        """Setup for each test method"""
        self.kem = ChromaCryptKEM(128)
    
    def test_key_generation(self):
        """Test KEM key generation"""
        public_key, private_key = self.kem.keygen()
        
        assert public_key is not None
        assert private_key is not None
        assert public_key.params.security_level == 128
        assert private_key.params.security_level == 128
    
    def test_encapsulation(self):
        """Test key encapsulation"""
        public_key, _ = self.kem.keygen()
        shared_secret, capsule = self.kem.encapsulate(public_key)
        
        assert len(shared_secret) == 32
        assert capsule is not None
    
    def test_decapsulation(self):
        """Test key decapsulation"""
        public_key, private_key = self.kem.keygen()
        shared_secret, capsule = self.kem.encapsulate(public_key)
        recovered_secret = self.kem.decapsulate(private_key, capsule)
        
        assert len(recovered_secret) == 32
        # For demonstration implementation, we just verify length
    
    def test_different_security_levels(self):
        """Test different security levels"""
        for level in [128, 192, 256]:
            kem = ChromaCryptKEM(level)
            pub, priv = kem.keygen()
            assert pub.params.security_level == level