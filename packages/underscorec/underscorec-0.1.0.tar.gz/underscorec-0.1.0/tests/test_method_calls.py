"""
Test method calls and attribute access operations.

These tests cover the GETATTR and METHOD_CALL operations implemented
in the C++ code, testing the create_method_call functionality.
"""
import pytest
from underscorec import __


class TestAttributeAccess:
    """Test attribute access via GETATTR operation."""
    
    def test_simple_attribute_access(self):
        """Test accessing simple attributes."""
        # String attributes
        expr = __.upper
        result = expr("hello")
        assert callable(result)  # Should return the method object
        
        # List attributes
        expr = __.append
        test_list = [1, 2, 3]
        result = expr(test_list)
        assert callable(result)  # Should return the method object
        
    def test_attribute_access_representation(self):
        """Test representation of attribute access."""
        assert repr(__.upper) == "__.upper"
        assert repr(__.split) == "__.split"
        assert repr(__.append) == "__.append"
        assert repr(__.count) == "__.count"
        
    def test_nonexistent_attribute_error(self):
        """Test that calling nonexistent methods raises AttributeError."""
        expr = __.nonexistent_method()
        with pytest.raises(AttributeError):
            expr("hello")
            
    def test_attribute_access_on_different_types(self):
        """Test attribute access on various object types."""
        # String method - note that GET_ATTR returns the method to be called
        expr = __.upper()  # Need to call it
        assert expr("hello") == "HELLO"
        
        # List method - need to call the method directly
        test_list = [1, 2]
        (__.append(3))(test_list)  # Calling append with argument
        assert test_list == [1, 2, 3]
        
        # Dict method - call it directly
        test_dict = {'a': 1, 'b': 2}
        assert (__.get('a'))(test_dict) == 1
        assert (__.get('c', 'default'))(test_dict) == 'default'


class TestMethodCalls:
    """Test method call operations (METHOD_CALL)."""
    
    def test_no_args_method_calls(self):
        """Test method calls without arguments."""
        # String methods
        assert (__.upper())("hello") == "HELLO"
        assert (__.lower())("HELLO") == "hello"
        assert (__.strip())("  hello  ") == "hello"
        assert (__.capitalize())("hello world") == "Hello world"
        
        # List methods
        test_list = [3, 1, 4, 1, 5]
        copied_list = test_list.copy()
        (__.sort())(copied_list)
        assert copied_list == [1, 1, 3, 4, 5]
        
        assert (__.copy())([1, 2, 3]) == [1, 2, 3]
        
    def test_single_arg_method_calls(self):
        """Test method calls with single argument."""
        # String methods
        assert (__.count("l"))("hello") == 2
        assert (__.count("x"))("hello") == 0
        assert (__.index("l"))("hello") == 2
        
        # String replacement
        assert (__.replace("l", "x"))("hello") == "hexxo"
        assert (__.replace("hello", "world"))("hello test") == "world test"
        
        # String splitting
        assert (__.split(","))("a,b,c") == ["a", "b", "c"]
        assert (__.split())("hello world test") == ["hello", "world", "test"]
        
    def test_multiple_args_method_calls(self):
        """Test method calls with multiple arguments."""
        # String methods with multiple args
        assert (__.replace("l", "x", 1))("hello") == "hexlo"
        assert (__.split(",", 1))("a,b,c") == ["a", "b,c"]
        
        # String formatting-related methods
        assert (__.center(10, "*"))("hi") == "****hi****"
        assert (__.ljust(10, "-"))("hello") == "hello-----"
        assert (__.rjust(10, "-"))("hello") == "-----hello"
        
    def test_keyword_args_method_calls(self):
        """Test method calls with keyword arguments."""
        # String methods with keyword arguments (split does support them)
        assert (__.split(sep=","))("a,b,c") == ["a", "b", "c"]
        assert (__.split(sep=",", maxsplit=1))("a,b,c") == ["a", "b,c"]
        
        # Test with list methods that support kwargs (like sort)
        test_list = [3, 1, 2]
        (__.sort(reverse=True))(test_list)
        assert test_list == [3, 2, 1]
        
    def test_mixed_args_kwargs_method_calls(self):
        """Test method calls with both positional and keyword arguments."""
        # This tests the full method call functionality using split which supports both
        assert (__.split(",", maxsplit=1))("a,b,c,d") == ["a", "b,c,d"]
        
        # Another mixed args example
        assert (__.replace("l", "x", 1))("hello world") == "hexlo world"
        
    def test_method_call_representation(self):
        """Test representation of method calls."""
        assert repr(__.upper()) == "__.upper()"
        assert repr(__.split(",")) == "__.split(',',)"
        assert repr(__.replace("a", "b")) == "__.replace('a', 'b')"
        assert repr(__.count("x")) == "__.count('x',)"
        
    def test_method_calls_on_lists(self):
        """Test method calls on list objects."""
        # Test append (modifies in place, returns None)
        test_list = [1, 2, 3]
        result = (__.append(4))(test_list)
        assert result is None
        assert test_list == [1, 2, 3, 4]
        
        # Test extend
        test_list = [1, 2]
        result = (__.extend([3, 4]))(test_list)
        assert result is None
        assert test_list == [1, 2, 3, 4]
        
        # Test insert
        test_list = [1, 3]
        result = (__.insert(1, 2))(test_list)
        assert result is None
        assert test_list == [1, 2, 3]
        
        # Test remove
        test_list = [1, 2, 3, 2]
        result = (__.remove(2))(test_list)
        assert result is None
        assert test_list == [1, 3, 2]  # Only first occurrence removed
        
        # Test pop
        test_list = [1, 2, 3]
        assert (__.pop())(test_list) == 3
        assert test_list == [1, 2]
        
        assert (__.pop(0))(test_list) == 1
        assert test_list == [2]
        
        # Test index and count
        test_list = [1, 2, 3, 2, 4]
        assert (__.index(2))(test_list) == 1
        assert (__.count(2))(test_list) == 2
        
    def test_method_calls_on_dicts(self):
        """Test method calls on dictionary objects."""
        # Test get method
        test_dict = {'a': 1, 'b': 2}
        assert (__.get('a'))(test_dict) == 1
        assert (__.get('c'))(test_dict) is None
        assert (__.get('c', 'default'))(test_dict) == 'default'
        
        # Test keys, values, items
        test_dict = {'a': 1, 'b': 2}
        keys = list((__.keys())(test_dict))
        assert sorted(keys) == ['a', 'b']
        
        values = list((__.values())(test_dict))
        assert sorted(values) == [1, 2]
        
        items = list((__.items())(test_dict))
        assert sorted(items) == [('a', 1), ('b', 2)]
        
        # Test pop
        test_dict = {'a': 1, 'b': 2}
        assert (__.pop('a'))(test_dict) == 1
        assert test_dict == {'b': 2}
        
        assert (__.pop('c', 'default'))(test_dict) == 'default'
        
        # Test update
        test_dict = {'a': 1}
        result = (__.update({'b': 2, 'c': 3}))(test_dict)
        assert result is None
        assert test_dict == {'a': 1, 'b': 2, 'c': 3}
        
    def test_chained_attribute_access(self):
        """Test chaining multiple attribute accesses."""
        # This should create a chain of GETATTR operations
        expr = __.strip().upper()
        assert expr("  hello  ") == "HELLO"
        
        expr = __.split(",")[0].upper()
        assert expr("hello,world") == "HELLO"
        
        expr = __.replace("l", "x").upper()
        assert expr("hello") == "HEXXO"
        
    def test_chained_method_representation(self):
        """Test representation of chained method calls."""
        assert repr(__.upper().lower()) == "__.upper().lower()"
        assert repr(__.strip().split()) == "__.strip().split()"
        assert repr(__.replace("a", "b").upper()) == "__.replace('a', 'b').upper()"
        
    def test_method_error_handling(self):
        """Test error handling in method calls."""
        # Non-existent method
        with pytest.raises(AttributeError):
            (__.nonexistent_method())("hello")
        
        # Wrong number of arguments
        with pytest.raises(TypeError):
            (__.replace())("hello")  # replace requires at least 2 args
            
        # Wrong argument types
        with pytest.raises(TypeError):
            (__.count(123))("hello")  # count expects string argument
        
        # Method that doesn't exist on the object type
        with pytest.raises(AttributeError):
            (__.upper())([1, 2, 3])  # lists don't have upper method


class TestComplexMethodScenarios:
    """Test complex scenarios involving method calls."""
    
    def test_method_calls_with_special_characters(self):
        """Test method calls with special characters and edge cases."""
        # Empty strings
        assert (__.upper())("") == ""
        assert (__.split(","))("") == [""]
        assert (__.replace("a", "b"))("") == ""
        
        # Unicode strings
        assert (__.upper())("héllo") == "HÉLLO"
        assert (__.lower())("HÉLLO") == "héllo"
        
        # Strings with special characters
        assert (__.split("|"))("a|b|c") == ["a", "b", "c"]
        assert (__.replace("\n", " "))("hello\nworld") == "hello world"
        
    def test_method_calls_with_none_results(self):
        """Test methods that return None."""
        # List methods that modify in place
        test_list = [1, 2, 3]
        assert (__.append(4))(test_list) is None
        assert (__.clear())(test_list) is None
        assert (__.reverse())([1, 2, 3]) is None
        
    def test_method_calls_with_exceptions(self):
        """Test methods that can raise exceptions."""
        # String index with substring not found
        with pytest.raises(ValueError):
            (__.index("x"))("hello")
        
        # List pop on empty list
        with pytest.raises(IndexError):
            (__.pop())([])
        
        # List remove with item not in list
        with pytest.raises(ValueError):
            (__.remove(5))([1, 2, 3])
        
    def test_nested_method_calls(self):
        """Test complex nested method scenarios."""
        # This tests method chaining with indexing
        expr = __.split(",")[1].strip().upper()
        assert expr("hello, world ") == "WORLD"
        
        # Method call followed by arithmetic
        test_list = [1, 2, 3, 4, 5]
        expr = __.count(3) + 10
        assert expr(test_list) == 11  # count returns 1, plus 10
        
    def test_method_calls_preserve_object_state(self):
        """Test that method calls properly preserve object state."""
        # Ensure that calling a method doesn't modify the expression
        expr = __.upper()
        
        result1 = expr("hello")
        result2 = expr("world")
        
        assert result1 == "HELLO"
        assert result2 == "WORLD"
        
        # The expression should be reusable
        assert expr("test") == "TEST"
        
    def test_method_calls_with_default_arguments(self):
        """Test method calls where some arguments have defaults."""
        # split() with no arguments uses any whitespace
        assert (__.split())("hello world\ttest") == ["hello", "world", "test"]
        
        # split() with sep but no maxsplit
        assert (__.split(","))("a,b,c,d") == ["a", "b", "c", "d"]
        
        # rsplit vs split
        assert (__.split(",", 1))("a,b,c") == ["a", "b,c"]
        
    def test_property_vs_method_smart_detection(self):
        """Test the smart detection of properties vs methods in GETATTR operations."""
        # Test with a custom class that has both properties and methods
        class TestObject:
            def __init__(self, value):
                self._value = value
                
            @property
            def value_prop(self):
                return self._value
                
            def get_value(self):
                return self._value
                
            def double_value(self):
                return self._value * 2
        
        obj = TestObject(42)
        
        # Test property access (non-callable) - should execute GETATTR directly
        prop_expr = __.value_prop
        prop_result = prop_expr(obj)
        assert prop_result == 42
        
        # Test method calls (callable) - should convert to METHOD_CALL
        method_expr = __.get_value()
        method_result = method_expr(obj)
        assert method_result == 42
        
        double_expr = __.double_value()
        double_result = double_expr(obj)
        assert double_result == 84
        
        # Test mixed property access and method calls in composition
        complex_expr = __.value_prop >> str >> __.upper()
        complex_result = complex_expr(obj)
        assert complex_result == "42"