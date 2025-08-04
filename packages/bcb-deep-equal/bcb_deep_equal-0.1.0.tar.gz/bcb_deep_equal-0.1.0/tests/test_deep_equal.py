"""
Tests for deep_equal function.
"""

import math
import pytest
from bcb_deep_equal import deep_equal, deep_equal_simple


class TestFloatingPointComparison:
    """Test floating-point comparison functionality."""
    
    def test_basic_float_precision(self):
        """Test the classic 0.1 + 0.2 != 0.3 problem."""
        assert deep_equal(0.1 + 0.2, 0.3)
        assert not (0.1 + 0.2 == 0.3)  # Standard comparison fails
        
    def test_division_multiplication(self):
        """Test division and multiplication precision issues."""
        assert deep_equal(1.0 / 3.0 * 3.0, 1.0)
        assert deep_equal(0.1 * 10, 1.0)
        
    def test_accumulation_errors(self):
        """Test accumulation of floating-point errors."""
        assert deep_equal(sum([0.1] * 10), 1.0)
        assert deep_equal(sum([0.01] * 100), 1.0)
        
    def test_custom_tolerances(self):
        """Test with custom relative and absolute tolerances."""
        # Should be equal with default tolerance
        assert deep_equal(1.0000001, 1.0000002)
        
        # Should not be equal with stricter tolerance
        assert not deep_equal(1.0000001, 1.0000002, rel_tol=1e-8)
        
        # Should be equal with looser tolerance
        assert deep_equal(1.01, 1.02, rel_tol=0.1)


class TestSpecialValues:
    """Test IEEE 754 special values."""
    
    def test_nan_comparison(self):
        """Test NaN comparison (NaN == NaN should be True)."""
        nan1 = float('nan')
        nan2 = float('nan')
        
        assert not (nan1 == nan2)  # Standard comparison
        assert deep_equal(nan1, nan2)  # Our comparison
        assert deep_equal(math.nan, math.nan)
        
    def test_infinity_comparison(self):
        """Test infinity comparison."""
        inf = float('inf')
        assert deep_equal(inf, inf)
        assert deep_equal(-inf, -inf)
        assert not deep_equal(inf, -inf)
        
    def test_mixed_special_values(self):
        """Test combinations of special values."""
        assert not deep_equal(float('nan'), float('inf'))
        assert not deep_equal(0.0, float('nan'))
        assert not deep_equal(1.0, float('inf'))


class TestContainerTypes:
    """Test comparison of container types."""
    
    def test_lists_with_floats(self):
        """Test lists containing floating-point values."""
        list1 = [0.1 + 0.2, 0.3 + 0.4]
        list2 = [0.3, 0.7]
        assert deep_equal(list1, list2)
        
        # Nested lists
        nested1 = [[0.1 + 0.2], [0.3 + 0.4]]
        nested2 = [[0.3], [0.7]]
        assert deep_equal(nested1, nested2)
        
    def test_dictionaries_with_floats(self):
        """Test dictionaries containing floating-point values."""
        dict1 = {'a': 0.1 + 0.2, 'b': 0.3 + 0.4}
        dict2 = {'a': 0.3, 'b': 0.7}
        assert deep_equal(dict1, dict2)
        
        # Nested dictionaries
        nested1 = {'results': {'x': 0.1 + 0.2, 'y': 0.3 + 0.4}}
        nested2 = {'results': {'x': 0.3, 'y': 0.7}}
        assert deep_equal(nested1, nested2)
        
    def test_mixed_containers(self):
        """Test mixed container types."""
        mixed1 = {
            'values': [0.1 + 0.2, 0.3 + 0.4],
            'total': 1.0,
            'metadata': {'count': 2}
        }
        mixed2 = {
            'values': [0.3, 0.7],
            'total': sum([0.3, 0.7]),
            'metadata': {'count': 2}
        }
        assert deep_equal(mixed1, mixed2)
        
    def test_sets_with_floats(self):
        """Test sets containing floating-point values."""
        set1 = {0.1 + 0.2, 0.3 + 0.4}
        set2 = {0.3, 0.7}
        assert deep_equal(set1, set2)
        
    def test_tuples_with_floats(self):
        """Test tuples containing floating-point values."""
        tuple1 = (0.1 + 0.2, 0.3 + 0.4)
        tuple2 = (0.3, 0.7)
        assert deep_equal(tuple1, tuple2)


class TestMixedTypes:
    """Test comparison of mixed numeric types."""
    
    def test_int_float_comparison(self):
        """Test comparison between integers and floats."""
        assert deep_equal(1, 1.0)
        assert deep_equal(42, 42.0)
        assert deep_equal(0, 0.0)
        
    def test_large_integers(self):
        """Test large integer comparison."""
        large_int = 2**53 + 1  # Beyond JavaScript safe integer
        assert deep_equal(large_int, large_int)
        assert deep_equal(large_int, float(large_int))
        
    def test_complex_numbers(self):
        """Test complex number comparison."""
        assert deep_equal(1+2j, 1+2j)
        assert deep_equal(0.1+0.2j, 0.1+0.2j)
        assert not deep_equal(1+2j, 1+3j)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_none_comparison(self):
        """Test None value comparison."""
        assert deep_equal(None, None)
        assert not deep_equal(None, 0)
        assert not deep_equal(0, None)
        
    def test_different_types(self):
        """Test comparison of different types."""
        assert not deep_equal(1.0, "1.0")
        assert not deep_equal([1.0], (1.0,))
        assert not deep_equal({1.0}, [1.0])
        
    def test_circular_references(self):
        """Test handling of circular references."""
        # Create circular reference
        list1 = [1, 2]
        list1.append(list1)
        
        list2 = [1, 2]
        list2.append(list2)
        
        # Should handle circular references without infinite recursion
        assert deep_equal(list1, list2)
        
    def test_very_large_numbers(self):
        """Test very large floating-point numbers."""
        large1 = 1e200
        large2 = 1e200 * (1 + 1e-7)
        assert deep_equal(large1, large2)
        
    def test_very_small_numbers(self):
        """Test very small floating-point numbers."""
        small1 = 1e-200
        small2 = 1e-200 * (1 + 1e-7)
        assert deep_equal(small1, small2)


class TestDeepEqualSimple:
    """Test the simplified deep_equal_simple function."""
    
    def test_basic_functionality(self):
        """Test basic functionality of deep_equal_simple."""
        assert deep_equal_simple(0.1 + 0.2, 0.3)
        assert deep_equal_simple([0.1 + 0.2], [0.3])
        assert deep_equal_simple({'a': 0.1 + 0.2}, {'a': 0.3})
        
    def test_nan_handling(self):
        """Test NaN handling in simple version."""
        assert deep_equal_simple(float('nan'), float('nan'))
        
    def test_no_numpy_dependency(self):
        """Test that simple version doesn't require numpy."""
        # This should work even if numpy is not installed
        result = deep_equal_simple([1.0, 2.0], [1.0, 2.0])
        assert result


class TestBCBIntegration:
    """Test scenarios specific to BigCodeBench integration."""
    
    def test_typical_bcb_outputs(self):
        """Test typical outputs from BCB tasks."""
        # Mathematical computations
        assert deep_equal(
            {'result': 0.1 + 0.2, 'status': 'ok'},
            {'result': 0.3, 'status': 'ok'}
        )
        
        # Array processing
        assert deep_equal(
            [sum([0.1] * i) for i in range(5)],
            [0.0, 0.1, 0.2, 0.3, 0.4]
        )
        
        # Statistical calculations
        mean1 = sum([0.1, 0.2, 0.3]) / 3
        mean2 = 0.2
        assert deep_equal(mean1, mean2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])