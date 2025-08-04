"""
Pytest configuration and fixtures for UnderscoreC tests.
"""
import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from underscorec import __


@pytest.fixture
def underscore():
    """Basic underscore instance."""
    return __




@pytest.fixture
def numpy_data():
    """NumPy arrays for testing (only if NumPy is available)."""
    if not HAS_NUMPY:
        pytest.skip("NumPy not available")
    
    return {
        'int_array': np.array([1, 2, 3, 4, 5]),
        'float_array': np.array([1.1, 2.2, 3.3, 4.4, 5.5]),
        'bool_array': np.array([True, False, True, False, True]),
        'matrix': np.array([[1, 2], [3, 4]]),
        'scalar': np.int32(42)
    }


@pytest.fixture
def torch_data():
    """PyTorch tensors for testing (only if PyTorch is available)."""
    if not HAS_TORCH:
        pytest.skip("PyTorch not available")
    
    return {
        'int_tensor': torch.tensor([1, 2, 3, 4, 5]),
        'float_tensor': torch.tensor([1.1, 2.2, 3.3, 4.4, 5.5]),
        'bool_tensor': torch.tensor([True, False, True, False, True]),
        'matrix': torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
        'scalar': torch.tensor(42.0)
    }


# Test parametrization helpers
@pytest.fixture(params=[
    1, 2, 3, 5, 10, 100, -1, -5, 0
])
def test_integers(request):
    """Parametrized test integers."""
    return request.param


@pytest.fixture(params=[
    1.0, 2.5, 3.14, -1.5, 0.0, 1e-10, 1e10
])
def test_floats(request):
    """Parametrized test floats."""
    return request.param


@pytest.fixture(params=[
    'hello', 'world', '', 'a', 'test string', '123', 'unicode: 🚀'
])
def test_strings(request):
    """Parametrized test strings."""
    return request.param


# Binary operation test data
@pytest.fixture
def binary_ops_data():
    """Data for binary operations testing."""
    return [
        # (operand, test_value, expected_result, description)
        (5, 10, 15, 'integer addition'),
        (2.5, 7.5, 10.0, 'float addition'),
        ('world', 'hello', 'helloworld', 'string concatenation'),
        ([3, 4], [1, 2], [1, 2, 3, 4], 'list concatenation')
    ]


@pytest.fixture
def comparison_ops_data():
    """Data for comparison operations testing."""
    return [
        # (operand, test_value, expected_gt, expected_lt, expected_eq, expected_ne, expected_ge, expected_le)
        (5, 10, True, False, False, True, True, False),
        (10, 5, False, True, False, True, False, True),
        (5, 5, False, False, True, False, True, True),
        (3.14, 2.71, False, True, False, True, False, True)
    ]


@pytest.fixture
def method_test_data():
    """Data for method call testing."""
    return [
        # (method_name, args, kwargs, test_input, expected_output, description)
        ('upper', (), {}, 'hello', 'HELLO', 'string upper'),
        ('lower', (), {}, 'HELLO', 'hello', 'string lower'),
        ('replace', ('l', 'x'), {}, 'hello', 'hexxo', 'string replace'),
        ('split', (',',), {}, 'a,b,c', ['a', 'b', 'c'], 'string split'),
        ('strip', (), {}, '  hello  ', 'hello', 'string strip'),
        ('count', ('l',), {}, 'hello', 2, 'string count'),
        ('startswith', ('he',), {}, 'hello', True, 'string startswith'),
        ('endswith', ('lo',), {}, 'hello', True, 'string endswith')
    ]


# Mark helpers for conditional tests
numpy_only = pytest.mark.skipif(not HAS_NUMPY, reason="NumPy not available")
torch_only = pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
slow_test = pytest.mark.slow  # For performance tests