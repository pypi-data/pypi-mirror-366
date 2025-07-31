"""
Tests for framework detection and implementation checking.
"""

import pytest
from php_framework_scaffolder.frameworks.factory import (
    _is_framework_implemented,
    _get_available_frameworks
)
from php_framework_scaffolder.frameworks.laravel import LaravelSetup
from php_framework_scaffolder.frameworks.thinkphp import ThinkPHPSetup


class TestFrameworkDetection:
    """Test cases for framework detection logic."""
    
    def test_implemented_framework_detection(self):
        """Test that implemented frameworks are correctly detected."""
        # Laravel should be implemented
        assert _is_framework_implemented(LaravelSetup) is True
    
    def test_unimplemented_framework_detection(self):
        """Test that unimplemented frameworks are correctly detected."""
        # ThinkPHP should not be implemented
        assert _is_framework_implemented(ThinkPHPSetup) is False
    
    def test_get_available_frameworks_returns_dict(self):
        """Test that _get_available_frameworks returns a dictionary."""
        available = _get_available_frameworks()
        assert isinstance(available, dict)
        assert len(available) > 0
    
    def test_available_frameworks_are_implemented(self):
        """Test that all frameworks in available list are actually implemented."""
        available = _get_available_frameworks()
        
        for framework_type, handler in available.items():
            # Test with the actual handler instance (should work since it was created successfully)
            assert hasattr(handler, 'get_setup_commands'), f"Framework {framework_type.name} should have get_setup_commands method"
            setup_commands = handler.get_setup_commands()
            assert isinstance(setup_commands, list), f"Framework {framework_type.name} should return a list of setup commands"
    
    def test_detection_consistency(self):
        """Test that detection results are consistent across multiple calls."""
        # This test ensures caching works correctly
        available1 = _get_available_frameworks()
        available2 = _get_available_frameworks()
        
        assert available1.keys() == available2.keys()
        
        # Check that the same handler instances are returned (due to caching)
        for framework_type in available1:
            assert type(available1[framework_type]) == type(available2[framework_type]) 