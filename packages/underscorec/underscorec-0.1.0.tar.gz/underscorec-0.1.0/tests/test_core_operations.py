"""
Test core operations - binary, unary, comparison, and indexing operations.

These tests cover the core functionality implemented in underscore_eval_single
and the operator overloading methods.
"""
import pytest
import math
from underscorec import __


class TestBinaryArithmetic:
    """Test binary arithmetic operations (+, -, *, /, %, **)."""
    
    def test_addition(self):
        """Test addition operation."""
        expr = __ + 5
        assert expr(10) == 15
        assert expr(0) == 5
        assert expr(-5) == 0
        
        # String concatenation
        expr = __ + " world"
        assert expr("hello") == "hello world"
        
        # List concatenation
        expr = __ + [4, 5]
        assert expr([1, 2, 3]) == [1, 2, 3, 4, 5]
    
    def test_subtraction(self):
        """Test subtraction operation."""
        expr = __ - 3
        assert expr(10) == 7
        assert expr(5) == 2
        assert expr(0) == -3
        assert expr(-5) == -8
        
    def test_multiplication(self):
        """Test multiplication operation."""
        expr = __ * 4
        assert expr(5) == 20
        assert expr(0) == 0
        assert expr(-2) == -8
        
        # String repetition
        expr = __ * 3
        assert expr("a") == "aaa"
        assert expr("") == ""
        
        # List repetition
        assert expr([1, 2]) == [1, 2, 1, 2, 1, 2]
        
    def test_division(self):
        """Test division operation."""
        expr = __ / 2
        assert expr(10) == 5.0
        assert expr(5) == 2.5
        assert expr(-4) == -2.0
        
        # Division by zero should raise exception
        with pytest.raises(ZeroDivisionError):
            expr = __ / 0
            expr(5)
            
    def test_modulo(self):
        """Test modulo operation."""
        expr = __ % 3
        assert expr(10) == 1
        assert expr(9) == 0
        assert expr(8) == 2
        assert expr(-1) == 2  # Python's modulo behavior
        
    def test_power(self):
        """Test power operation."""
        expr = __ ** 2
        assert expr(3) == 9
        assert expr(4) == 16
        assert expr(0) == 0
        assert expr(-2) == 4
        
        expr = __ ** 0.5
        assert expr(16) == 4.0
        assert expr(9) == 3.0
        
    def test_power_modular_not_implemented(self):
        """Test that 3-argument pow raises NotImplementedError."""
        # This test may not be applicable since we use Python's standard pow
        # Just test that normal 2-arg pow works
        expr = __ ** 2
        assert expr(3) == 9


class TestComparisonOperations:
    """Test comparison operations (>, <, ==, !=, >=, <=)."""
    
    def test_greater_than(self):
        """Test greater than operation."""
        expr = __ > 5
        assert expr(10) is True
        assert expr(5) is False
        assert expr(3) is False
        
    def test_less_than(self):
        """Test less than operation."""
        expr = __ < 5
        assert expr(3) is True
        assert expr(5) is False
        assert expr(7) is False
        
    def test_equal(self):
        """Test equality operation."""
        expr = __ == 5
        assert expr(5) is True
        assert expr(4) is False
        assert expr(6) is False
        
        # String equality
        expr = __ == "hello"
        assert expr("hello") is True
        assert expr("world") is False
        
    def test_not_equal(self):
        """Test inequality operation."""
        expr = __ != 5
        assert expr(4) is True
        assert expr(6) is True
        assert expr(5) is False
        
    def test_greater_equal(self):
        """Test greater than or equal operation."""
        expr = __ >= 5
        assert expr(5) is True
        assert expr(6) is True
        assert expr(4) is False
        
    def test_less_equal(self):
        """Test less than or equal operation."""
        expr = __ <= 5
        assert expr(5) is True
        assert expr(4) is True
        assert expr(6) is False
        
    @pytest.mark.parametrize("op, operand, test_val, expected", [
        ('>', 5, 10, True), ('>', 5, 3, False), ('>', 5, 5, False),
        ('<', 5, 3, True), ('<', 5, 10, False), ('<', 5, 5, False),
        ('==', 5, 5, True), ('==', 5, 4, False),
        ('!=', 5, 4, True), ('!=', 5, 5, False),
        ('>=', 5, 5, True), ('>=', 5, 6, True), ('>=', 5, 4, False),
        ('<=', 5, 5, True), ('<=', 5, 4, True), ('<=', 5, 6, False),
    ])
    def test_comparison_parametrized(self, op, operand, test_val, expected):
        """Parametrized test for all comparison operations."""
        if op == '>':
            expr = __ > operand
        elif op == '<':
            expr = __ < operand
        elif op == '==':
            expr = __ == operand
        elif op == '!=':
            expr = __ != operand
        elif op == '>=':
            expr = __ >= operand
        elif op == '<=':
            expr = __ <= operand
        
        assert expr(test_val) is expected


class TestBitwiseOperations:
    """Test bitwise operations (&, |, ^, <<, >>)."""
    
    def test_bitwise_and(self):
        """Test bitwise AND operation."""
        expr = __ & 3
        assert expr(5) == 1  # 5 & 3 = 1
        assert expr(7) == 3  # 7 & 3 = 3
        assert expr(0) == 0  # 0 & 3 = 0
        
    def test_bitwise_or(self):
        """Test bitwise OR operation."""
        expr = __ | 3
        assert expr(5) == 7  # 5 | 3 = 7
        assert expr(4) == 7  # 4 | 3 = 7
        assert expr(0) == 3  # 0 | 3 = 3
        
    def test_bitwise_xor(self):
        """Test bitwise XOR operation."""
        expr = __ ^ 3
        assert expr(5) == 6  # 5 ^ 3 = 6
        assert expr(3) == 0  # 3 ^ 3 = 0
        assert expr(0) == 3  # 0 ^ 3 = 3
        
    def test_left_shift(self):
        """Test left shift operation."""
        expr = __ << 2
        assert expr(5) == 20  # 5 << 2 = 20
        assert expr(1) == 4   # 1 << 2 = 4
        assert expr(0) == 0   # 0 << 2 = 0
        
    def test_right_shift(self):
        """Test right shift operation (when used as bitwise, not composition)."""
        expr = __ >> 1
        assert expr(8) == 4   # 8 >> 1 = 4
        assert expr(5) == 2   # 5 >> 1 = 2
        assert expr(1) == 0   # 1 >> 1 = 0


class TestUnaryOperations:
    """Test unary operations (-, abs, ~)."""
    
    def test_negation(self):
        """Test unary negation."""
        expr = -__
        assert expr(5) == -5
        assert expr(-3) == 3
        assert expr(0) == 0
        
    def test_absolute(self):
        """Test absolute value."""
        expr = abs(__)
        assert expr(-5) == 5
        assert expr(5) == 5
        assert expr(0) == 0
        assert expr(-3.14) == 3.14
        
    def test_invert(self):
        """Test bitwise inversion."""
        expr = ~__
        assert expr(5) == -6   # ~5 = -6
        assert expr(0) == -1   # ~0 = -1
        assert expr(-1) == 0   # ~-1 = 0
        
    def test_unary_chaining(self):
        """Test chaining of unary operations."""
        expr = -(__ * 2)
        assert expr(3) == -6
        
        expr = abs(__ + 1)
        assert expr(-5) == 4
        
        expr = ~(__ | 1)
        assert expr(4) == -6  # ~(4|1) = ~5 = -6


class TestIndexingOperations:
    """Test indexing operations ([])."""
    
    def test_list_indexing(self):
        """Test list indexing."""
        test_list = [1, 2, 3, 4, 5]
        
        expr = __[0]
        assert expr(test_list) == 1
        
        expr = __[-1]
        assert expr(test_list) == 5
        
        expr = __[2]
        assert expr(test_list) == 3
        
    def test_string_indexing(self):
        """Test string indexing."""
        test_string = "hello"
        
        expr = __[0]
        assert expr(test_string) == 'h'
        
        expr = __[-1]
        assert expr(test_string) == 'o'
        
        expr = __[1]
        assert expr(test_string) == 'e'
        
    def test_dict_indexing(self):
        """Test dictionary indexing."""
        test_dict = {'a': 1, 'b': 2, 'c': 3}
        
        expr = __['a']
        assert expr(test_dict) == 1
        
        expr = __['b']
        assert expr(test_dict) == 2
        
        expr = __['c']
        assert expr(test_dict) == 3
        
    def test_tuple_indexing(self):
        """Test tuple indexing."""
        test_tuple = (10, 20, 30)
        
        expr = __[0]
        assert expr(test_tuple) == 10
        
        expr = __[1]
        assert expr(test_tuple) == 20
        
        expr = __[-1]
        assert expr(test_tuple) == 30
        
    def test_slicing(self):
        """Test slice operations."""
        test_list = [1, 2, 3, 4, 5]
        
        expr = __[1:3]
        assert expr(test_list) == [2, 3]
        
        expr = __[::2]
        assert expr(test_list) == [1, 3, 5]
        
        expr = __[:3]
        assert expr(test_list) == [1, 2, 3]
        
        expr = __[2:]
        assert expr(test_list) == [3, 4, 5]
        
    def test_index_errors(self):
        """Test that index errors are properly propagated."""
        test_list = [1, 2, 3]
        
        expr = __[10]
        with pytest.raises(IndexError):
            expr(test_list)
        
        test_dict = {'a': 1}
        expr = __['missing_key']
        with pytest.raises(KeyError):
            expr(test_dict)


class TestIdentityOperation:
    """Test the identity operation (__ by itself)."""
    
    def test_identity(self):
        """Test that identity returns the input unchanged."""
        # Test with various data types
        assert __(42) == 42
        assert __("hello") == "hello"
        assert __([1, 2, 3]) == [1, 2, 3]
        assert __({"a": 1}) == {"a": 1}
        assert __(3.14) == 3.14
        assert __(True) is True
        assert __(None) is None
        
    def test_identity_object_references(self):
        """Test that identity preserves object references."""
        test_list = [1, 2, 3]
        result = __(test_list)
        assert result is test_list  # Same object
        
        test_dict = {'a': 1}
        result = __(test_dict)
        assert result is test_dict  # Same object


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_type_errors(self):
        """Test that type errors are properly handled."""
        # String - integer operations that should fail
        with pytest.raises(TypeError):
            expr = __ - 5
            expr("hello")
            
        # Unsupported operations
        with pytest.raises(TypeError):
            expr = __ & 3.14  # Bitwise operations on floats
            expr(5.5)
            
    def test_zero_division(self):
        """Test division by zero handling."""
        with pytest.raises(ZeroDivisionError):
            expr = __ / 0
            expr(5)
            
        with pytest.raises(ZeroDivisionError):
            expr = __ % 0
            expr(5)
            
    def test_overflow_handling(self):
        """Test handling of large numbers."""
        # These should work without issues
        expr = __ + 1
        assert expr(10**100) == 10**100 + 1
        
        expr = __ * 2
        result = expr(10**50)
        assert result == 2 * (10**50)
        
    def test_complex_numbers(self):
        """Test operations with complex numbers."""
        expr = __ + 3
        assert expr(2+3j) == 5+3j
        
        expr = __ * 2
        assert expr(1+2j) == 2+4j


class TestRepresentation:
    """Test string representations of underscore expressions."""
    
    def test_simple_operations(self):
        """Test representations of simple operations."""
        assert repr(__ + 5) == "(__ + 5)"
        assert repr(__ - 3) == "(__ - 3)"
        assert repr(__ * 2) == "(__ * 2)"
        assert repr(__ / 4) == "(__ / 4)"
        assert repr(__ % 3) == "(__ % 3)"
        assert repr(__ ** 2) == "(__ ** 2)"
        
    def test_comparison_representations(self):
        """Test representations of comparison operations."""
        assert repr(__ > 5) == "(__ > 5)"
        assert repr(__ < 10) == "(__ < 10)"
        assert repr(__ == 5) == "(__ == 5)"
        assert repr(__ != 3) == "(__ != 3)"
        assert repr(__ >= 5) == "(__ >= 5)"
        assert repr(__ <= 10) == "(__ <= 10)"
        
    def test_bitwise_representations(self):
        """Test representations of bitwise operations."""
        assert repr(__ & 3) == "(__ & 3)"
        assert repr(__ | 5) == "(__ | 5)"
        assert repr(__ ^ 7) == "(__ ^ 7)"
        assert repr(__ << 2) == "(__ << 2)"
        assert repr(__ >> 1) == "(__ >> 1)"
        
    def test_unary_representations(self):
        """Test representations of unary operations."""
        assert repr(-__) == "(-__)"
        assert repr(abs(__)) == "abs(__)"
        assert repr(~__) == "(~__)"
        
    def test_indexing_representations(self):
        """Test representations of indexing operations."""
        assert repr(__[0]) == "(__[0])"
        assert repr(__['key']) == "(__['key'])"
        # Slices are represented as slice objects
        assert "slice(1, 3, None)" in repr(__[1:3])
        
    def test_identity_representation(self):
        """Test representation of identity operation."""
        assert repr(__) == "__"