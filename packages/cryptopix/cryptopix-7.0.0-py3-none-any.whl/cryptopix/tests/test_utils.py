"""
Test suite for utility functions.
"""

import pytest
from ..utils.validation import (
    validate_security_level, 
    validate_color_format, 
    validate_password_strength
)
from ..utils.performance import PerformanceProfiler, enable_optimizations

class TestValidation:
    
    def test_security_level_validation(self):
        """Test security level validation"""
        assert validate_security_level(128) is True
        assert validate_security_level(192) is True
        assert validate_security_level(256) is True
        assert validate_security_level(127) is False
        assert validate_security_level(512) is False
    
    def test_color_format_validation(self):
        """Test color format validation"""
        assert validate_color_format((255, 128, 0)) is True
        assert validate_color_format((0, 0, 0)) is True
        assert validate_color_format((255, 255, 255)) is True
        assert validate_color_format((256, 128, 0)) is False
        assert validate_color_format((-1, 128, 0)) is False
        assert validate_color_format((255, 128)) is False
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        strong_password = "StrongPass123!"
        weak_password = "weak"
        
        is_strong, issues_strong = validate_password_strength(strong_password)
        is_weak, issues_weak = validate_password_strength(weak_password)
        
        assert len(issues_weak) > 0
        # Strong password should have fewer issues

class TestPerformance:
    
    def test_profiler_creation(self):
        """Test performance profiler creation"""
        profiler = PerformanceProfiler()
        assert profiler is not None
    
    def test_enable_optimizations(self):
        """Test optimization enablement"""
        optimizations = enable_optimizations()
        
        assert 'numba_available' in optimizations
        assert 'numpy_version' in optimizations
        assert 'enabled_optimizations' in optimizations
        assert isinstance(optimizations['enabled_optimizations'], list)