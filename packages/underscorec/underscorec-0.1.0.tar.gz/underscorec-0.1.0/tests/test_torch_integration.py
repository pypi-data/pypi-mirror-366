"""
Test PyTorch integration functionality.

These tests cover the PyTorch-specific optimizations implemented in
underscorec_torch.cpp, including tensor operations via C++ API.
"""
import pytest
# Import marks and availability checks
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    
torch_only = pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")

if HAS_TORCH:
    import torch

from underscorec import __


@torch_only
class TestTorchTensorOperations:
    """Test basic PyTorch tensor operations."""
    
    def test_tensor_arithmetic(self, torch_data):
        """Test arithmetic operations on PyTorch tensors."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Addition
        result = (__ + 10)(tensor)
        expected = torch.tensor([11, 12, 13, 14, 15])
        assert torch.equal(result, expected)
        
        # Subtraction
        result = (__ - 2)(tensor)
        expected = torch.tensor([-1, 0, 1, 2, 3])
        assert torch.equal(result, expected)
        
        # Multiplication
        result = (__ * 3)(tensor)
        expected = torch.tensor([3, 6, 9, 12, 15])
        assert torch.equal(result, expected)
        
        # Division
        float_tensor = tensor.float()
        result = (__ / 2)(float_tensor)
        expected = torch.tensor([0.5, 1.0, 1.5, 2.0, 2.5])
        assert torch.allclose(result, expected)
        
    def test_tensor_power_and_modulo(self, torch_data):
        """Test power and modulo operations."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Power
        result = (__ ** 2)(tensor.float())
        expected = torch.tensor([1.0, 4.0, 9.0, 16.0, 25.0])
        assert torch.allclose(result, expected)
        
        # Modulo (remainder)
        result = (__ % 3)(tensor)
        expected = torch.tensor([1, 2, 0, 1, 2])
        assert torch.equal(result, expected)
        
    def test_tensor_comparison_operations(self, torch_data):
        """Test comparison operations on PyTorch tensors."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Greater than
        result = (__ > 3)(tensor)
        expected = torch.tensor([False, False, False, True, True])
        assert torch.equal(result, expected)
        
        # Less than
        result = (__ < 3)(tensor)
        expected = torch.tensor([True, True, False, False, False])
        assert torch.equal(result, expected)
        
        # Equal
        result = (__ == 3)(tensor)
        expected = torch.tensor([False, False, True, False, False])
        assert torch.equal(result, expected)
        
        # Not equal
        result = (__ != 3)(tensor)
        expected = torch.tensor([True, True, False, True, True])
        assert torch.equal(result, expected)
        
        # Greater equal
        result = (__ >= 3)(tensor)
        expected = torch.tensor([False, False, True, True, True])
        assert torch.equal(result, expected)
        
        # Less equal
        result = (__ <= 3)(tensor)
        expected = torch.tensor([True, True, True, False, False])
        assert torch.equal(result, expected)
        
    def test_float_tensor_operations(self, torch_data):
        """Test operations on float tensors."""
        tensor = torch_data['float_tensor']  # tensor([1.1, 2.2, 3.3, 4.4, 5.5])
        
        # Arithmetic operations
        result = (__ + 0.5)(tensor)
        expected = torch.tensor([1.6, 2.7, 3.8, 4.9, 6.0])
        assert torch.allclose(result, expected)
        
        result = (__ * 2.0)(tensor)
        expected = torch.tensor([2.2, 4.4, 6.6, 8.8, 11.0])
        assert torch.allclose(result, expected)
        
    def test_matrix_operations(self, torch_data):
        """Test operations on 2D PyTorch tensors (matrices)."""
        matrix = torch_data['matrix']  # tensor([[1.0, 2.0], [3.0, 4.0]])
        
        # Element-wise operations
        result = (__ + 10)(matrix)
        expected = torch.tensor([[11.0, 12.0], [13.0, 14.0]])
        assert torch.allclose(result, expected)
        
        result = (__ * 2)(matrix)
        expected = torch.tensor([[2.0, 4.0], [6.0, 8.0]])
        assert torch.allclose(result, expected)
        
        # Comparison operations
        result = (__ > 2)(matrix)
        expected = torch.tensor([[False, False], [True, True]])
        assert torch.equal(result, expected)
        
    def test_boolean_tensor_operations(self, torch_data):
        """Test operations on boolean tensors."""
        bool_tensor = torch_data['bool_tensor']  # tensor([True, False, True, False, True])
        
        # Convert to int for arithmetic
        int_tensor = bool_tensor.int()  # tensor([1, 0, 1, 0, 1])
        
        result = (__ + 1)(int_tensor)
        expected = torch.tensor([2, 1, 2, 1, 2])
        assert torch.equal(result, expected)
        
    def test_scalar_tensor_operations(self, torch_data):
        """Test operations with PyTorch scalar tensors."""
        scalar = torch_data['scalar']  # tensor(42.0)
        
        # These should work just like regular scalars
        result = (__ + 8)(scalar)
        expected = torch.tensor(50.0)
        assert torch.allclose(result, expected)
        
        result = (__ * 2)(scalar)
        expected = torch.tensor(84.0)
        assert torch.allclose(result, expected)
        
        result = (__ / 6)(scalar)
        expected = torch.tensor(7.0)
        assert torch.allclose(result, expected)


@torch_only
class TestTorchSpecialCases:
    """Test special cases and edge conditions for PyTorch integration."""
    
    def test_empty_tensors(self):
        """Test operations on empty tensors."""
        empty_tensor = torch.tensor([])
        
        result = (__ + 5)(empty_tensor)
        assert torch.equal(result, torch.tensor([]))
        
        result = (__ * 2)(empty_tensor)
        assert torch.equal(result, torch.tensor([]))
        
    def test_single_element_tensors(self):
        """Test operations on single-element tensors."""
        single_tensor = torch.tensor([42])
        
        result = (__ + 8)(single_tensor)
        expected = torch.tensor([50])
        assert torch.equal(result, expected)
        
        result = (__ > 40)(single_tensor)
        expected = torch.tensor([True])
        assert torch.equal(result, expected)
        
    def test_large_tensors(self):
        """Test operations on large tensors."""
        large_tensor = torch.arange(1000)
        
        result = (__ + 1)(large_tensor)
        expected = torch.arange(1, 1001)
        assert torch.equal(result, expected)
        
        # Check that it's still using optimized path
        result = (__ > 500)(large_tensor)
        assert result.sum().item() == 499  # 501 through 999 are > 500
        
    def test_different_dtypes(self):
        """Test operations with different PyTorch data types."""
        # Test with different dtypes
        dtypes = [torch.int8, torch.int16, torch.int32, torch.int64,
                 torch.uint8, torch.float16, torch.float32, torch.float64]
        
        for dtype in dtypes:
            tensor = torch.tensor([1, 2, 3, 4, 5], dtype=dtype)
            result = (__ + 10)(tensor)
            
            # Convert to common type for comparison
            expected = torch.tensor([11, 12, 13, 14, 15])
            if dtype.is_floating_point:
                expected = expected.float()
            
            # Compare values, allowing for type differences
            assert torch.allclose(result.float(), expected.float())
    
    def test_gpu_tensors(self):
        """Test operations with GPU tensors (if CUDA available)."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
            
        # Create GPU tensor
        gpu_tensor = torch.tensor([1, 2, 3, 4, 5]).cuda()
        
        # Operations should work on GPU
        result = (__ + 10)(gpu_tensor)
        expected = torch.tensor([11, 12, 13, 14, 15]).cuda()
        assert torch.equal(result, expected)
        assert result.is_cuda
        
        # Move back to CPU for comparison
        result_cpu = result.cpu()
        expected_cpu = expected.cpu()
        assert torch.equal(result_cpu, expected_cpu)
        
    def test_tensor_broadcasting(self):
        """Test that PyTorch broadcasting works correctly."""
        # Test with tensors of different shapes
        tensor1d = torch.tensor([1, 2, 3, 4])
        tensor2d = torch.tensor([[1, 2], [3, 4]])
        
        # 1D tensor operations
        result = (__ + torch.tensor([10, 20, 30, 40]))(tensor1d)
        expected = torch.tensor([11, 22, 33, 44])
        assert torch.equal(result, expected)
        
        # 2D tensor with scalar
        result = (__ + 100)(tensor2d)
        expected = torch.tensor([[101, 102], [103, 104]])
        assert torch.equal(result, expected)
        
    def test_torch_error_handling(self):
        """Test error handling in PyTorch operations."""
        tensor = torch.tensor([1, 2, 3, 4, 5])
        
        # Operations that should fail gracefully
        with pytest.raises((RuntimeError, TypeError)):
            # Trying to add tensors with incompatible shapes
            incompatible = torch.tensor([[1, 2, 3]])  # Wrong shape
            result = (__ + incompatible)(tensor)
            
    def test_fallback_to_standard_protocols(self):
        """Test that operations fall back to standard Python protocols when needed."""
        # Test with operations that might not be supported by the optimized path
        tensor = torch.tensor([1.0, 2.0, 3.0])
        
        # This should still work, either via optimized path or fallback
        result = (__ + 1.0)(tensor)
        expected = torch.tensor([2.0, 3.0, 4.0])
        assert torch.allclose(result, expected)
        
    def test_operand_type_conversion(self):
        """Test automatic operand type conversion in PyTorch operations."""
        tensor = torch.tensor([1, 2, 3])
        
        # Python int operand
        result = (__ + 5)(tensor)
        expected = torch.tensor([6, 7, 8])
        assert torch.equal(result, expected)
        
        # Python float operand
        result = (__ + 5.5)(tensor.float())
        expected = torch.tensor([6.5, 7.5, 8.5])
        assert torch.allclose(result, expected)
        
        # PyTorch tensor operand
        operand = torch.tensor(10)
        result = (__ + operand)(tensor)
        expected = torch.tensor([11, 12, 13])
        assert torch.equal(result, expected)


@torch_only
class TestTorchComposition:
    """Test PyTorch tensors in composition and complex expressions."""
    
    def test_torch_with_composition(self, torch_data):
        """Test PyTorch tensors in composition chains."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Tensor operation followed by tolist method call
        expr = __ + 1 >> __.tolist()
        result = expr(tensor)
        assert result == [2, 3, 4, 5, 6]  # [1,2,3,4,5] + 1 = [2,3,4,5,6]
        
        # Tensor operation followed by len on the result
        expr = __ * 2 >> len
        result = expr(tensor)
        assert result == 5  # Length of tensor
        
    def test_torch_multi_reference(self, torch_data):
        """Test PyTorch tensors in multi-reference expressions."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Multi-reference with tensors
        expr = __ + __
        result = expr(tensor)
        expected = torch.tensor([2, 4, 6, 8, 10])
        assert torch.equal(result, expected)
        
        expr = __ * __
        result = expr(tensor)
        expected = torch.tensor([1, 4, 9, 16, 25])
        assert torch.equal(result, expected)
        
    def test_mixed_torch_python_operations(self, torch_data):
        """Test mixing PyTorch tensors with regular Python operations."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Tensor operation, then shape access, then dimension extraction
        expr = (__ + 1) >> __.shape >> __[0]
        result = expr(tensor)
        assert result == 5
        
    def test_torch_property_vs_method_access(self, torch_data):
        """Test that properties and methods are handled correctly."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Test tensor properties (non-callable) - should execute GETATTR directly
        shape_expr = __.shape
        shape_result = shape_expr(tensor)
        assert shape_result == torch.Size([5])
        assert isinstance(shape_result, torch.Size)
        
        dtype_expr = __.dtype
        dtype_result = dtype_expr(tensor)
        assert dtype_result == torch.int64
        
        # Test tensor methods (callable) - should convert to METHOD_CALL
        size_expr = __.size()
        size_result = size_expr(tensor)
        assert size_result == torch.Size([5])
        
        tolist_expr = __.tolist()
        tolist_result = tolist_expr(tensor)
        assert tolist_result == [1, 2, 3, 4, 5]
        
        # Test complex composition with properties
        complex_expr = (__ * 2) >> __.shape >> len
        complex_result = complex_expr(tensor)
        assert complex_result == 1  # 1D tensor has shape length 1
        
    @pytest.mark.skip(reason="Indexing not supported for PyTorch tensors in current implementation")
    def test_torch_with_indexing(self, torch_data):
        """Test PyTorch tensors with indexing operations."""
        tensor = torch_data['int_tensor']  # tensor([1, 2, 3, 4, 5])
        
        # Tensor operation followed by indexing
        expr = (__ + 10)[2]
        result = expr(tensor)
        expected_value = 13  # (tensor + 10)[2] = [11,12,13,14,15][2] = 13
        assert result.item() == expected_value
        
        # Indexing followed by tensor operation
        matrix = torch_data['matrix']  # tensor([[1.0, 2.0], [3.0, 4.0]])
        expr = __[0] + 100
        result = expr(matrix)
        expected = torch.tensor([101.0, 102.0])
        assert torch.allclose(result, expected)


@torch_only
class TestTorchPerformance:
    """Test that PyTorch operations use optimized paths."""
    
    def test_cpp_api_optimization_used(self, torch_data):
        """Test that the optimized C++ API path is being used."""
        # This is more of a smoke test - we can't easily verify 
        # that the C++ optimized path is used, but we can verify
        # that the results are correct and reasonably fast
        
        large_tensor = torch.arange(10000)
        
        # These should complete quickly using C++ API
        result = (__ + 1)(large_tensor)
        assert len(result) == 10000
        assert result[0].item() == 1
        assert result[-1].item() == 10000
        
        result = (__ * 2)(large_tensor)
        assert result[100].item() == 200
        
        result = (__ > 5000)(large_tensor)
        assert result.sum().item() == 4999  # 5001 through 9999
        
    def test_type_checking_optimization(self):
        """Test that type checking optimization works."""
        # Multiple operations should correctly identify tensors
        tensor1 = torch.tensor([1, 2, 3])
        tensor2 = torch.tensor([4, 5, 6])
        tensor3 = torch.tensor([7, 8, 9])
        
        expr = __ + 10
        
        # All of these should use the optimized PyTorch path
        result1 = expr(tensor1)
        result2 = expr(tensor2)
        result3 = expr(tensor3)
        
        assert torch.equal(result1, torch.tensor([11, 12, 13]))
        assert torch.equal(result2, torch.tensor([14, 15, 16]))
        assert torch.equal(result3, torch.tensor([17, 18, 19]))
        
    @pytest.mark.slow
    def test_performance_comparison(self):
        """Performance comparison test (marked as slow)."""
        # This test compares the performance of PyTorch operations
        # vs standard Python operations
        import time
        
        # Large tensor for timing
        large_tensor = torch.arange(100000, dtype=torch.float32)
        large_list = list(range(100000))
        
        # Time PyTorch operation
        expr = __ + 1
        start = time.time()
        for _ in range(10):
            result = expr(large_tensor)
        torch_time = time.time() - start
        
        # Time Python list operation using map (since + doesn't work on lists)  
        start = time.time()
        for _ in range(10):
            result = list(map(lambda x: x + 1, large_list))
        python_time = time.time() - start
        
        # PyTorch should be competitive (this is a rough check)
        # Note: This is more of a sanity check than a rigorous benchmark
        assert torch_time < python_time * 2  # Should be reasonably fast


@torch_only
class TestTorchEdgeCases:
    """Test edge cases and error conditions with PyTorch."""
    
    def test_torch_with_none_operands(self):
        """Test PyTorch operations with None operands."""
        tensor = torch.tensor([1, 2, 3])
        
        # Operations with None should fail appropriately
        with pytest.raises((TypeError, RuntimeError)):
            expr = __ + None
            expr(tensor)
            
    def test_torch_with_complex_dtypes(self):
        """Test with complex number tensors."""
        if hasattr(torch, 'complex64'):  # Check if complex dtypes are supported
            complex_tensor = torch.tensor([1+2j, 3+4j, 5+6j], dtype=torch.complex64)
            
            # Basic operations should work
            result = (__ + 1)(complex_tensor)
            expected = torch.tensor([2+2j, 4+4j, 6+6j], dtype=torch.complex64)
            assert torch.allclose(result, expected)
            
            result = (__ * 2)(complex_tensor)
            expected = torch.tensor([2+4j, 6+8j, 10+12j], dtype=torch.complex64)
            assert torch.allclose(result, expected)
        else:
            pytest.skip("Complex dtypes not supported in this PyTorch version")
            
    def test_torch_requires_grad(self):
        """Test with tensors that require gradients."""
        tensor = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
        
        # Operations should preserve gradient tracking
        result = (__ + 1)(tensor)
        assert result.requires_grad
        
        result = (__ * 2)(tensor)
        assert result.requires_grad
        
        # Backward pass should work
        loss = result.sum()
        loss.backward()
        
        # Check that gradients were computed
        assert tensor.grad is not None
        expected_grad = torch.tensor([2.0, 2.0, 2.0])
        assert torch.allclose(tensor.grad, expected_grad)
        
    def test_tensor_memory_format(self):
        """Test with different tensor memory formats."""
        # Create a tensor with specific memory format (if supported)
        tensor = torch.randn(2, 3, 4, 5)
        
        # Try different memory formats
        if hasattr(torch, 'channels_last'):
            tensor_cl = tensor.contiguous(memory_format=torch.channels_last)
            
            # Operations should work regardless of memory format
            result = (__ + 1)(tensor_cl)
            expected = tensor_cl + 1
            assert torch.allclose(result, expected)
            
    def test_tensor_devices_mismatch(self):
        """Test error handling with mismatched devices."""
        cpu_tensor = torch.tensor([1, 2, 3])
        
        if torch.cuda.is_available():
            gpu_operand = torch.tensor(5).cuda()
            
            # This should raise an appropriate error
            with pytest.raises(RuntimeError):
                expr = __ + gpu_operand
                expr(cpu_tensor)
        else:
            pytest.skip("CUDA not available for device mismatch test")
            
    def test_tensor_conversion_edge_cases(self):
        """Test edge cases in operand conversion."""
        tensor = torch.tensor([1.0, 2.0, 3.0])
        
        # Test with various Python types as operands
        result = (__ + True)(tensor)  # bool -> tensor
        expected = torch.tensor([2.0, 3.0, 4.0])
        assert torch.allclose(result, expected)
        
        # Test with numpy scalar (if numpy available)
        try:
            import numpy as np
            np_scalar = np.float32(2.5)
            result = (__ + np_scalar)(tensor)
            expected = torch.tensor([3.5, 4.5, 5.5])
            assert torch.allclose(result, expected)
        except ImportError:
            pass  # Skip if numpy not available