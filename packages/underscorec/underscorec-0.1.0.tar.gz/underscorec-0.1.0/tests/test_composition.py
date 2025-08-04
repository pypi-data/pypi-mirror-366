"""
Test function composition and multi-reference expressions.

These tests cover the composition chains (next_expr) and multi-reference
expressions (left_expr/right_expr) functionality.
"""
import pytest
import math
from underscorec import __


class TestFunctionComposition:
    """Test function composition using >> operator (FUNCTION_CALL)."""
    
    def test_basic_composition(self):
        """Test basic function composition."""
        # Simple composition: add then convert to string
        expr = __ + 1 >> str
        assert expr(5) == "6"
        assert expr(0) == "1"
        assert expr(-1) == "0"
        
        # Composition with abs
        expr = __ + 1 >> abs
        assert expr(-5) == 4
        assert expr(-2) == 1
        assert expr(5) == 6
        
    def test_multiple_composition(self):
        """Test composition with multiple functions."""
        # Chain: add, abs, str
        expr = __ + 1 >> abs >> str
        assert expr(-5) == "4"
        assert expr(-2) == "1"
        assert expr(5) == "6"
        
        # Chain: multiply, abs, str, len
        expr = __ * -2 >> abs >> str >> len
        assert expr(5) == 2  # -10 -> 10 -> "10" -> 2
        assert expr(50) == 3  # -100 -> 100 -> "100" -> 3
        
    def test_composition_with_builtin_functions(self):
        """Test composition with various builtin functions."""
        # Test with len
        expr = __ >> len
        assert expr("hello") == 5
        assert expr([1, 2, 3, 4]) == 4
        assert expr({}) == 0
        
        # Test with int
        expr = __ >> int
        assert expr("42") == 42
        assert expr(3.14) == 3
        assert expr(True) == 1
        
        # Test with float
        expr = __ >> float
        assert expr("3.14") == 3.14
        assert expr(42) == 42.0
        
        # Test with bool
        expr = __ >> bool
        assert expr(1) is True
        assert expr(0) is False
        assert expr("") is False
        assert expr("hello") is True
        
    def test_composition_with_math_functions(self):
        """Test composition with math module functions."""
        # Test with math.sqrt
        expr = __ >> math.sqrt
        assert expr(16) == 4.0
        assert expr(9) == 3.0
        assert expr(0) == 0.0
        
        # Test with math.sin
        expr = __ >> math.sin
        result = expr(math.pi / 2)
        assert abs(result - 1.0) < 1e-10
        
        # Test with math.log
        expr = __ >> math.log
        result = expr(math.e)
        assert abs(result - 1.0) < 1e-10
        
        # Chained math operations
        expr = __ * 2 >> math.sin >> abs
        result = expr(math.pi / 4)
        expected = abs(math.sin(math.pi / 4 * 2))
        assert abs(result - expected) < 1e-10
        
    def test_composition_with_method_calls(self):
        """Test composition involving method calls."""
        # Method call followed by function
        expr = __.upper() >> len
        assert expr("hello") == 5
        assert expr("") == 0
        
        # Arithmetic followed by method call
        expr = __ * 2 >> str >> __.upper()
        assert expr(21) == "42"
        
        # Complex chain
        expr = __.split(",") >> len >> __ + 1
        assert expr("a,b,c") == 4  # ["a","b","c"] -> 3 -> 4
        
    def test_composition_representation(self):
        """Test string representation of composition."""
        expr = __ + 1 >> str
        assert "(__ + 1) >> <class 'str'>" == repr(expr)
        
        expr = __ >> abs >> str
        assert "__ >> <built-in function abs> >> <class 'str'>" == repr(expr)
        
    def test_composition_with_lambdas(self):
        """Test composition with lambda functions."""
        # Simple lambda
        double = lambda x: x * 2
        expr = __ + 1 >> double
        assert expr(5) == 12  # (5 + 1) * 2 = 12
        
        # Multiple lambdas
        add_one = lambda x: x + 1
        square = lambda x: x * x
        expr = __ >> add_one >> square
        assert expr(3) == 16  # 3 -> 4 -> 16
        
    def test_composition_error_propagation(self):
        """Test that errors in composition are properly propagated."""
        # Division by zero in composition
        with pytest.raises(ZeroDivisionError):
            expr = __ >> (lambda x: 1 / x)
            expr(0)
        
        # Type error in composition
        with pytest.raises(AttributeError):
            expr = __ >> len >> __.upper()  # Can't call upper on int
            expr("hello")
        
        # Math domain error
        with pytest.raises(ValueError):
            expr = __ >> math.sqrt
            expr(-1)


class TestMultiReferenceExpressions:
    """Test multi-reference expressions (__ OP __)."""
    
    def test_basic_multi_reference(self):
        """Test basic multi-reference operations."""
        # Addition: __ + __
        expr = __ + __
        assert expr(5) == 10  # 5 + 5 = 10
        assert expr(0) == 0   # 0 + 0 = 0
        assert expr(-3) == -6 # -3 + -3 = -6
        
        # Multiplication: __ * __
        expr = __ * __
        assert expr(4) == 16  # 4 * 4 = 16
        assert expr(0) == 0   # 0 * 0 = 0
        assert expr(-2) == 4  # -2 * -2 = 4
        
    def test_all_multi_reference_operations(self):
        """Test all binary operations in multi-reference form."""
        test_val = 6
        
        # Arithmetic operations
        assert (__ + __)(test_val) == 12   # 6 + 6
        assert (__ - __)(test_val) == 0    # 6 - 6  
        assert (__ * __)(test_val) == 36   # 6 * 6
        assert (__ / __)(test_val) == 1.0  # 6 / 6
        assert (__ % __)(test_val) == 0    # 6 % 6
        assert (__ ** __)(test_val) == 46656  # 6 ** 6
        
        # Comparison operations
        assert (__ > __)(test_val) is False  # 6 > 6
        assert (__ < __)(test_val) is False  # 6 < 6
        assert (__ == __)(test_val) is True  # 6 == 6
        assert (__ != __)(test_val) is False # 6 != 6
        assert (__ >= __)(test_val) is True  # 6 >= 6
        assert (__ <= __)(test_val) is True  # 6 <= 6
        
        # Bitwise operations
        test_val = 5
        assert (__ & __)(test_val) == 5    # 5 & 5
        assert (__ | __)(test_val) == 5    # 5 | 5
        assert (__ ^ __)(test_val) == 0    # 5 ^ 5
        assert (__ << __)(test_val) == 160 # 5 << 5
        # __ >> __ is composition (identity >> identity), not bitwise shift
        assert (__ >> __)(test_val) == 5   # 5 >> identity function = 5
        
    def test_multi_reference_with_different_values(self):
        """Test multi-reference behavior with various input types."""
        # String concatenation
        expr = __ + __
        assert expr("hello") == "hellohello"
        assert expr("") == ""
        
        # List concatenation
        assert expr([1, 2]) == [1, 2, 1, 2]
        assert expr([]) == []
        
        # Tuple concatenation
        assert expr((1, 2)) == (1, 2, 1, 2)
        
    def test_multi_reference_with_composition(self):
        """Test multi-reference expressions combined with composition."""
        # Multi-reference with composition
        expr = (__ >> len) + (__ >> int)
        assert expr('123') == 126  # len('123') + int('123') = 3 + 123 = 126
        
        # More complex example
        expr = (__ + 1) * (__ - 1)
        assert expr(5) == 24  # (5+1) * (5-1) = 6 * 4 = 24
        assert expr(3) == 8   # (3+1) * (3-1) = 4 * 2 = 8
        
    def test_multi_reference_representation(self):
        """Test representation of multi-reference expressions."""
        assert repr(__ + __) == "__ + __"
        assert repr(__ * __) == "__ * __"
        assert repr(__ == __) == "__ == __"
        assert repr(__ & __) == "__ & __"
        
    def test_nested_multi_reference(self):
        """Test nested multi-reference expressions."""
        # This creates a more complex multi-reference structure
        left_expr = __ + 1
        right_expr = __ + 2
        expr = left_expr + right_expr  # (__ + 1) + (__ + 2)
        
        assert expr(5) == 13  # (5+1) + (5+2) = 6 + 7 = 13
        assert expr(0) == 3   # (0+1) + (0+2) = 1 + 2 = 3
        
    def test_multi_reference_error_handling(self):
        """Test error handling in multi-reference expressions."""
        # Type errors
        with pytest.raises(TypeError):
            expr = __ + __
            expr("hello", 123)  # This should fail - incorrect call
        
        # Division by zero
        with pytest.raises(ZeroDivisionError):
            expr = __ / __
            expr(0)
        
    def test_multi_reference_with_method_calls(self):
        """Test multi-reference with method calls."""
        # This is a complex case involving method calls in multi-ref
        expr = __.upper() + __.lower()
        # This would need the input to be duplicated and different methods applied
        # For a single input "Hello":  "hello" + "HELLO" = "helloHELLO"
        assert expr("Hello") == "helloHELLO"


class TestComplexCompositionScenarios:
    """Test complex scenarios involving both composition and multi-reference."""
    
    def test_composition_of_multi_reference(self):
        """Test composition applied to multi-reference expressions."""
        # (__ + __) >> str
        expr = (__ + __) >> str
        assert expr(5) == "10"
        assert expr(0) == "0"
        
        # (__ * __) >> abs >> str
        expr = (__ * __) >> abs >> str
        assert expr(-3) == "9"
        
    def test_multi_reference_of_compositions(self):
        """Test multi-reference where each side is a composition."""
        # (__ >> abs) + (__ >> abs)
        expr = (__ >> abs) + (__ >> abs)
        assert expr(-5) == 10  # abs(-5) + abs(-5) = 5 + 5 = 10
        assert expr(3) == 6    # abs(3) + abs(3) = 3 + 3 = 6
        
        # More complex
        expr = (__ + 1 >> abs) * (__ - 1 >> abs)
        assert expr(-2) == 3   # abs(-2+1) * abs(-2-1) = abs(-1) * abs(-3) = 1 * 3 = 3
        
    def test_deep_composition_chains(self):
        """Test deep composition chains."""
        # Very long chain
        expr = __ + 1 >> abs >> str >> len >> __ + 10 >> str >> len
        result = expr(-100)
        # -100 + 1 = -99 -> abs(-99) = 99 -> "99" -> len("99") = 2 
        # -> 2 + 10 = 12 -> "12" -> len("12") = 2
        assert result == 2
        
    def test_composition_with_side_effects(self):
        """Test composition with functions that have side effects."""
        # This tests that composition works even when functions modify state
        call_count = []
        
        def counting_func(x):
            call_count.append(x)
            return x * 2
        
        expr = __ + 1 >> counting_func >> __ + 5
        result = expr(10)
        
        assert result == 27  # (10 + 1) * 2 + 5 = 22 + 5 = 27
        assert call_count == [11]  # counting_func was called with 11
        
        # Call again to ensure it's reusable
        result = expr(5)
        assert result == 17  # (5 + 1) * 2 + 5 = 12 + 5 = 17
        assert call_count == [11, 6]  # now called with both values
        
    def test_composition_order_of_operations(self):
        """Test that composition respects proper order of operations."""
        # Test that >> has correct precedence
        expr = __ * 2 + 3 >> str  # Should be: (__ * 2 + 3) >> str, not __ * 2 + (3 >> str)
        assert expr(5) == "13"  # (5 * 2 + 3) = 13 -> "13"
        
        # Test with parentheses
        expr = (__ * 2) >> (lambda x: x + 3) >> str
        assert expr(5) == "13"  # (5 * 2) -> (10 + 3) -> "13"
        
    def test_composition_with_generator_functions(self):
        """Test composition with generator and iterator functions."""
        # Test with range
        expr = __ >> range >> list
        assert expr(3) == [0, 1, 2]
        assert expr(0) == []
        
        # Test with enumerate
        expr = __.split(",") >> enumerate >> list
        result = expr("a,b,c")
        assert result == [(0, 'a'), (1, 'b'), (2, 'c')]
        
    def test_composition_performance_characteristics(self):
        """Test that composition doesn't create excessive overhead."""
        # This is more of a sanity check than a rigorous performance test
        # Long composition chain
        expr = __ + 1 >> abs >> (lambda x: x * 2) >> str >> len >> float >> int
        
        # Should complete without issues
        result = expr(5)
        assert result == 2  # (5+1) -> 6 -> 6 -> 12 -> "12" -> 2 -> 2.0 -> 2
        
    def test_error_propagation_in_complex_expressions(self):
        """Test error propagation in complex expressions."""
        # Error in multi-reference
        with pytest.raises(ZeroDivisionError):
            expr = (__ / 0) + (__  * 2)
            expr(5)
        
        # Error in composition chain
        with pytest.raises(ValueError):
            expr = __ >> int >> math.sqrt  # int() might fail, sqrt might fail
            expr("not_a_number")
        
        # Error propagation through multiple levels
        with pytest.raises(AttributeError):
            expr = (__ + __) >> __.upper()  # Can't call upper on int result
            expr(5)
