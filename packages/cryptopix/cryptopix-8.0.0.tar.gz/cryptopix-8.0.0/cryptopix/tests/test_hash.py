"""
Test suite for Color Hash functions.
"""

import pytest
from ..core.color_hash import ColorHash

class TestColorHash:
    
    def setup_method(self):
        """Setup for each test method"""
        self.hasher = ColorHash(128)
    
    def test_hash_to_colors(self):
        """Test hashing data to colors"""
        data = b"Test data for color hashing"
        colors = self.hasher.hash_to_colors(data)
        
        assert len(colors) > 0
        assert all(len(color) == 3 for color in colors)
        assert all(0 <= c <= 255 for color in colors for c in color)
    
    def test_hash_verification(self):
        """Test hash verification"""
        data = b"Verification test data"
        colors = self.hasher.hash_to_colors(data)
        
        is_valid = self.hasher.verify_hash(data, colors)
        assert is_valid is True
    
    def test_hex_string_hash(self):
        """Test hex string hash generation"""
        data = b"Hex hash test data"
        hex_hash = self.hasher.hash_to_hex_string(data)
        
        assert isinstance(hex_hash, str)
        assert len(hex_hash) > 0
        assert all(c in '0123456789abcdef' for c in hex_hash.lower())
    
    def test_different_data_produces_different_hashes(self):
        """Test that different data produces different hashes"""
        data1 = b"First test data"
        data2 = b"Second test data"
        
        colors1 = self.hasher.hash_to_colors(data1)
        colors2 = self.hasher.hash_to_colors(data2)
        
        # Hashes should be different (though this is probabilistic)
        assert colors1 != colors2
    
    def test_consistency(self):
        """Test that same data produces same hash"""
        data = b"Consistency test data"
        
        colors1 = self.hasher.hash_to_colors(data)
        colors2 = self.hasher.hash_to_colors(data)
        
        assert colors1 == colors2