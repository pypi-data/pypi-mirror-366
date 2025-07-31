#!/usr/bin/env python3
"""
Tests for the framework factory module.

This module tests the automatic framework detection and exception handling
in the framework factory.
"""

import pytest
from php_framework_scaffolder.frameworks.factory import get_framework_handler, get_supported_frameworks
from php_framework_detector.core.models import FrameworkType


class TestFrameworkFactory:
    """Test cases for the framework factory."""
    
    def test_get_supported_frameworks_returns_list(self, supported_frameworks):
        """Test that get_supported_frameworks returns a list of implemented frameworks."""
        assert isinstance(supported_frameworks, list)
        assert len(supported_frameworks) > 0
    
    def test_none_framework_raises_value_error(self):
        """Test that passing None raises ValueError."""
        with pytest.raises(ValueError, match="Framework type cannot be None"):
            get_framework_handler(None)
    
    def test_invalid_string_raises_value_error(self):
        """Test that passing invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid framework type.*Must be a FrameworkType enum value"):
            get_framework_handler("invalid_framework")
    
    def test_invalid_number_raises_value_error(self):
        """Test that passing invalid number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid framework type.*Must be a FrameworkType enum value"):
            get_framework_handler(123)
    
    def test_unimplemented_framework_raises_not_implemented_error(self, sample_unsupported_framework):
        """Test that unimplemented frameworks raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match=f"Framework '{sample_unsupported_framework.name}' is not implemented yet"):
            get_framework_handler(sample_unsupported_framework)
    
    def test_implemented_framework_returns_handler(self, sample_framework):
        """Test that implemented frameworks return valid handlers."""
        handler = get_framework_handler(sample_framework)
        assert handler is not None
        assert hasattr(handler, 'get_setup_commands')
        
        # Test that the handler can actually provide setup commands
        setup_commands = handler.get_setup_commands()
        assert isinstance(setup_commands, list)
    
    def test_all_supported_frameworks_have_setup_commands(self, supported_frameworks):
        """Test that all supported frameworks can provide setup commands."""
        for framework in supported_frameworks:
            handler = get_framework_handler(framework)
            setup_commands = handler.get_setup_commands()
            assert isinstance(setup_commands, list), f"Framework {framework.name} should return a list of setup commands"
            assert len(setup_commands) > 0, f"Framework {framework.name} should have at least one setup command"


# Manual testing functions for interactive use
def run_test_case(description, test_func):
    """Helper function for manual testing with console output."""
    print(f"\nTEST: {description}")
    print("-" * 60)
    try:
        result = test_func()
        print(f"SUCCESS: {result}")
        return True
    except ValueError as e:
        print(f"ValueError: {e}")
        return False
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False


def manual_test_suite():
    """Manual test suite for interactive testing."""
    print("Testing exception handling in framework factory")
    print("=" * 60)
    
    # Get supported frameworks for reference
    supported = get_supported_frameworks()
    all_frameworks = [ft for ft in FrameworkType]
    unsupported = [ft for ft in all_frameworks if ft not in supported]
    
    print(f"STATUS: {len(supported)} implemented, {len(unsupported)} not implemented")
    
    # Test cases
    run_test_case(
        "Test 1: Passing None as framework",
        lambda: get_framework_handler(None)
    )
    
    run_test_case(
        "Test 2: Passing invalid type (string)",
        lambda: get_framework_handler("invalid_framework")
    )
    
    run_test_case(
        "Test 3: Passing invalid type (number)",
        lambda: get_framework_handler(123)
    )
    
    if unsupported:
        test_framework = unsupported[0]
        run_test_case(
            f"Test 4: Valid but unimplemented framework ({test_framework.name})",
            lambda: get_framework_handler(test_framework)
        )
    else:
        print("\nTEST: Test 4: Valid but unimplemented framework")
        print("-" * 60)
        print("SKIPPED: All frameworks are implemented!")
    
    if supported:
        test_framework = supported[0]
        run_test_case(
            f"Test 5: Valid and implemented framework ({test_framework.name})",
            lambda: f"Handler: {type(get_framework_handler(test_framework)).__name__}"
        )
    
    print(f"\n{'=' * 60}")
    print("Exception handling test completed!")


if __name__ == "__main__":
    # If run directly, execute manual test suite
    manual_test_suite() 