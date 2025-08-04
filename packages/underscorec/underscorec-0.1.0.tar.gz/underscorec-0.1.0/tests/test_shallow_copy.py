"""
Test shallow copy bug fixes and deep copy functionality.

These tests verify that the deep_copy function properly handles
composition chains and multi-reference expressions to prevent
shallow copy bugs that could cause mutation issues.
"""
import pytest
from underscorec import __


class TestShallowCopyBugFixes:
    """Test that shallow copy bugs have been fixed."""
    
    def test_binary_operation_shallow_copy_fix(self):
        """Test that creating binary operations doesn't mutate original expressions."""
        # Create base expression
        expr1 = (__ + 1) * 2
        original_repr1 = repr(expr1)
        original_result1 = expr1(5)  # Should be (5 + 1) * 2 = 12
        
        # Create second expression from first - this should NOT mutate expr1
        expr2 = expr1 + 3
        expr2_result = expr2(5)  # Should be ((5 + 1) * 2) + 3 = 15
        
        # Check that expr1 is unchanged
        mutated_repr1 = repr(expr1)
        mutated_result1 = expr1(5)
        
        assert mutated_repr1 == original_repr1, "expr1 representation changed!"
        assert mutated_result1 == original_result1, "expr1 behavior changed!"
        assert expr2_result == 15, f"Expected 15, got {expr2_result}"
        
    def test_composition_shallow_copy_fix(self):
        """Test that creating compositions doesn't mutate original expressions."""
        # Test Case 1: Simple expression
        expr1 = __ + 1
        original_repr1 = repr(expr1)
        original_result1 = expr1(5)  # Should be 5 + 1 = 6
        
        # Create composition from first - this should NOT mutate expr1
        expr2 = expr1 >> str
        expr2_result = expr2(5)  # Should be str(5 + 1) = "6"
        
        # Check that expr1 is unchanged
        mutated_repr1 = repr(expr1)
        mutated_result1 = expr1(5)
        
        assert mutated_repr1 == original_repr1
        assert mutated_result1 == original_result1
        assert expr2_result == "6"
        
        # Test Case 2: Expression with existing composition chain
        expr3 = __ + 1 >> abs  # This creates a composition chain
        original_repr3 = repr(expr3)
        original_result3 = expr3(-5)  # Should be abs(-5 + 1) = abs(-4) = 4
        
        # Create another composition - this should NOT mutate expr3
        expr4 = expr3 >> str
        expr4_result = expr4(-5)  # Should be str(abs(-5 + 1)) = str(4) = "4"
        
        # Check that expr3 is unchanged
        mutated_repr3 = repr(expr3)
        mutated_result3 = expr3(-5)
        
        assert mutated_repr3 == original_repr3
        assert mutated_result3 == original_result3
        assert expr4_result == "4"
        
    def test_complex_composition_chain_shallow_copy(self):
        """Test complex composition chain shallow copy fix."""
        # Complex composition chain (most likely to trigger bug)
        expr5 = __ * 2 >> abs >> str >> len  # Multi-step composition
        original_repr5 = repr(expr5)
        original_result5 = expr5(-50)  # -50*2=-100 -> abs(-100)=100 -> "100" -> len("100")=3
        
        # Create composition from complex chain - this should NOT mutate expr5
        import math
        expr6 = expr5 >> float >> math.sqrt  # Should work: 3 -> 3.0 -> sqrt(3.0)
        expr6_result = expr6(-50)
        
        # Check that expr5 is unchanged
        mutated_repr5 = repr(expr5)
        mutated_result5 = expr5(-50)
        
        assert mutated_repr5 == original_repr5
        assert mutated_result5 == original_result5
        assert abs(expr6_result - math.sqrt(3.0)) < 1e-10
        
    def test_method_call_shallow_copy_fix(self):
        """Test that method calls don't cause shallow copy issues."""
        # Create expression with method
        expr1 = __.upper()
        original_repr1 = repr(expr1)
        original_result1 = expr1("hello")
        
        # Create chained method call - should not mutate expr1
        expr2 = expr1 >> __.lower()  # upper() then lower()
        expr2_result = expr2("hello")
        
        # Check expr1 unchanged
        mutated_repr1 = repr(expr1)
        mutated_result1 = expr1("hello")
        
        assert mutated_repr1 == original_repr1
        assert mutated_result1 == original_result1
        assert expr2_result == "hello"  # "hello" -> "HELLO" -> "hello"
        
    def test_multi_reference_shallow_copy_fix(self):
        """Test multi-reference expressions don't cause shallow copy issues."""
        # Create base expressions
        left = __ + 10
        right = __ + 20
        
        # Create multiref
        multiref = left * right  # (__ + 10) * (__ + 20)
        original_multiref_repr = repr(multiref)
        original_multiref_result = multiref(5)  # (5 + 10) * (5 + 20) = 15 * 25 = 375
        
        # Create further operations on the multiref - should not mutate original
        further1 = multiref + 100  
        further2 = multiref >> str
        
        # Check that multiref is unchanged
        current_multiref_repr = repr(multiref)
        current_multiref_result = multiref(5)
        
        assert current_multiref_repr == original_multiref_repr
        assert current_multiref_result == original_multiref_result
        
        # Check further operations work correctly
        assert further1(5) == 475  # 375 + 100
        assert further2(5) == "375"  # str(375)


class TestDeepCopyFunctionality:
    """Test the deep copy functionality directly."""
    
    def test_deep_copy_preserves_functionality(self):
        """Test that deep copied expressions work identically to originals."""
        # Create complex expression
        original = __ + 1 >> abs >> str >> len
        
        # Use the expression to create a new one (triggers deep copy)
        copied = original >> float
        
        # Both should work independently
        orig_result = original(-10)  # |-10+1| -> |9| -> "9" -> 1
        copy_result = copied(-10)   # Same as above, then float(1) -> 1.0
        
        assert orig_result == 1
        assert copy_result == 1.0
        
        # Test with different inputs
        assert original(100) == 3   # |100+1| -> "101" -> 3
        assert copied(100) == 3.0   # Same as above -> 3.0
        
    def test_deep_copy_with_multiple_references(self):
        """Test deep copy with expressions that have multiple references."""
        # Create expression used in multiple places
        base_expr = __ * 2 + 1
        
        # Create multiple expressions from the base
        expr1 = base_expr >> str
        expr2 = base_expr >> abs
        expr3 = base_expr + 10
        
        # All should work independently without interfering
        test_input = 5
        
        base_result = base_expr(test_input)     # 5*2+1 = 11
        expr1_result = expr1(test_input)        # str(11) = "11"
        expr2_result = expr2(test_input)        # abs(11) = 11
        expr3_result = expr3(test_input)        # 11 + 10 = 21
        
        assert base_result == 11
        assert expr1_result == "11"
        assert expr2_result == 11
        assert expr3_result == 21
        
        # Test with negative input
        test_input = -3
        
        base_result = base_expr(test_input)     # -3*2+1 = -5
        expr1_result = expr1(test_input)        # str(-5) = "-5"
        expr2_result = expr2(test_input)        # abs(-5) = 5
        expr3_result = expr3(test_input)        # -5 + 10 = 5
        
        assert base_result == -5
        assert expr1_result == "-5"
        assert expr2_result == 5
        assert expr3_result == 5
        
    def test_deep_copy_with_method_calls(self):
        """Test deep copy functionality with method calls."""
        # Create base expression with method
        base_expr = __.strip().upper()
        
        # Create variations
        expr1 = base_expr + " WORLD"
        expr2 = base_expr >> len
        
        test_input = "  hello  "
        
        base_result = base_expr(test_input)    # "  hello  ".strip().upper() = "HELLO"
        expr1_result = expr1(test_input)       # "HELLO" + " WORLD" = "HELLO WORLD"
        expr2_result = expr2(test_input)       # len("HELLO") = 5
        
        assert base_result == "HELLO"
        assert expr1_result == "HELLO WORLD"
        assert expr2_result == 5
        
    def test_deep_copy_recursion_safety(self):
        """Test that deep copy handles recursive structures safely."""
        # Create deeply nested expression
        expr = __
        for i in range(10):
            expr = expr + i >> abs
            
        # Create another expression from this deep one
        final_expr = expr >> str >> len
        
        # Should work without stack overflow or other issues
        result = final_expr(1)
        assert isinstance(result, int)
        assert result > 0
        
    def test_identity_deep_copy(self):
        """Test deep copy of identity expression."""
        # Identity should work correctly when copied
        identity = __
        
        # Create expression from identity
        expr = identity + 5
        
        # Both should work
        assert identity(10) == 10
        assert expr(10) == 15
        
        # Identity should remain unchanged
        assert identity(20) == 20
        assert expr(20) == 25


class TestMemoryManagement:
    """Test memory management and reference counting."""
    
    def test_reference_counting_in_deep_copy(self):
        """Test that reference counting works correctly with deep copy."""
        # Create objects that would be problematic if reference counting is wrong
        test_list = [1, 2, 3]
        
        # Create expression that references the list
        expr1 = __ + [4, 5]
        result1 = expr1(test_list)
        
        # Create another expression (triggers deep copy)
        expr2 = expr1 >> len
        result2 = expr2(test_list)
        
        # Original list should be unchanged
        assert test_list == [1, 2, 3]
        assert result1 == [1, 2, 3, 4, 5]
        assert result2 == 5
        
    def test_circular_reference_handling(self):
        """Test handling of potential circular references."""
        # This test ensures we don't create problematic circular references
        # in the C extension
        
        # Create multiple interrelated expressions
        expr1 = __ + 1
        expr2 = expr1 * 2
        expr3 = expr2 + expr1  # This could potentially create issues
        
        # All should work correctly
        assert expr1(5) == 6
        assert expr2(5) == 12
        assert expr3(5) == 18  # (5+1)*2 + (5+1) = 12 + 6 = 18
        
    def test_large_expression_tree_memory_usage(self):
        """Test memory usage with large expression trees."""
        # Create a large expression tree
        base = __
        for i in range(100):
            base = base + 1 >> abs if i % 2 == 0 else base * 2 >> str >> len
            
        # Create multiple copies
        copies = []
        for i in range(10):
            copies.append(base >> float)
            
        # All should work without memory issues
        for copy_expr in copies:
            result = copy_expr(1)
            assert isinstance(result, float)
            
    def test_expression_reuse_safety(self):
        """Test that expressions can be safely reused after deep copying."""
        # Create base expression
        base_expr = __ * 2 + 1
        
        # Create derived expressions
        derived1 = base_expr >> str
        derived2 = base_expr >> abs
        
        # Reuse base expression multiple times
        inputs = [1, 2, 3, 4, 5, -1, -2, -3]
        
        for inp in inputs:
            base_result = base_expr(inp)
            derived1_result = derived1(inp)
            derived2_result = derived2(inp)
            
            expected_base = inp * 2 + 1
            assert base_result == expected_base
            assert derived1_result == str(expected_base)
            assert derived2_result == abs(expected_base)


class TestErrorHandlingWithShallowCopy:
    """Test error handling doesn't interfere with shallow copy fixes."""
    
    def test_error_propagation_with_deep_copy(self):
        """Test that errors propagate correctly through deep copied expressions."""
        # Create expression that will cause error
        error_expr = __ / 0
        
        # Create derived expression (triggers deep copy)
        derived_expr = error_expr >> str
        
        # Both should raise the same error
        with pytest.raises(ZeroDivisionError):
            error_expr(5)
            
        with pytest.raises(ZeroDivisionError):
            derived_expr(5)
            
    def test_partial_failure_isolation(self):
        """Test that partial failures don't affect other expressions."""
        # Create base expression
        base_expr = __ + 1
        
        # Create one that will fail and one that will succeed
        fail_expr = base_expr / 0  # Will cause division by zero
        success_expr = base_expr * 2  # Will work fine
        
        # Success expression should work despite failure expression existing
        assert success_expr(5) == 12  # (5+1)*2
        
        # Failure expression should still fail correctly
        with pytest.raises(ZeroDivisionError):
            fail_expr(5)
            
        # Success expression should still work after failure
        assert success_expr(10) == 22  # (10+1)*2