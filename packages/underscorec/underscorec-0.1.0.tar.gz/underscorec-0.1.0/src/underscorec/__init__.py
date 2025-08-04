"""
UnderscoreC: C-based functional programming library for Python

Usage:
    from underscorec import __
    
    # Basic operations
    add_one = __ + 1
    result = add_one(5)  # Returns 6
    
    # With NumPy, PyTorch, Pandas
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    result = (__ * 2 + 1)(arr)  # Fast vectorized operations
"""

# Import PyTorch first to ensure libraries are loaded for C++ extension
import torch

from .underscorec import __

__all__ = ['__']
__version__ = "0.1.0"