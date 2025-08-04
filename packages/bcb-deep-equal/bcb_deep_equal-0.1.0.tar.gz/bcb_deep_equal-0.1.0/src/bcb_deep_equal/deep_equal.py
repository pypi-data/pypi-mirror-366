"""
Deep equality comparison with floating-point tolerance for BigCodeBench.

This module provides robust comparison functions that handle:
- Floating-point precision issues (e.g., 0.1 + 0.2 != 0.3)
- NumPy arrays and Pandas DataFrames
- IEEE 754 special values (NaN, infinity)
- Circular references
- Mixed numeric types
"""

import math
import logging
from typing import Any, Optional, Set, Tuple

# Optional imports with graceful degradation
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import pandas as pd
    import pandas.testing as pd_testing
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    pd_testing = None

logger = logging.getLogger(__name__)


def deep_equal(a: Any, b: Any, rel_tol: float = 1e-6, abs_tol: float = 1e-9, 
               _visited: Optional[Set[Tuple[int, int]]] = None, _depth: int = 0) -> bool:
    """
    Recursively checks the equality of two data structures with enhanced support for:
    - Floating-point comparisons with tolerance
    - NumPy arrays using np.allclose()
    - Pandas DataFrames/Series using pandas.testing
    - IEEE 754 special values (NaN, infinity)
    - Circular reference protection
    - Fallback to == operator for custom objects
    
    Args:
        a, b: Objects to compare
        rel_tol: Relative tolerance for floating-point comparisons (default: 1e-6)
        abs_tol: Absolute tolerance for floating-point comparisons (default: 1e-9)
        _visited: Internal parameter for circular reference detection
        _depth: Internal parameter for recursion depth tracking
        
    Returns:
        bool: True if objects are equal within tolerance, False otherwise
        
    Examples:
        >>> deep_equal(0.1 + 0.2, 0.3)  # Fixes floating-point precision
        True
        >>> deep_equal(float('nan'), float('nan'))  # NaN comparison
        True
        >>> deep_equal([1.0, 2.0], [1.0, 2.0])  # List comparison
        True
    """
    # Recursion depth protection
    MAX_RECURSION_DEPTH = 100
    if _depth > MAX_RECURSION_DEPTH:
        logger.warning(f"Maximum recursion depth {MAX_RECURSION_DEPTH} exceeded in deep_equal")
        return False
    
    # Initialize visited set for circular reference detection
    if _visited is None:
        _visited = set()
    
    # Fast path: identity check
    if a is b:
        return True
    
    # Handle None values
    if a is None or b is None:
        return a is b
    
    # Handle floating-point numbers with NaN support and edge cases
    if isinstance(a, float) and isinstance(b, float):
        # NaN == NaN should be True in our comparison
        if math.isnan(a) and math.isnan(b):
            return True
        # Handle infinity
        if math.isinf(a) and math.isinf(b):
            return a == b  # This checks if both are +inf or both are -inf
        
        # Handle very large/small numbers with logarithmic comparison
        # This prevents overflow/underflow in relative tolerance calculation
        if abs(a) > 1e100 or abs(b) > 1e100:
            # For very large numbers, use logarithmic comparison if both are positive
            if a > 0 and b > 0:
                return abs(math.log10(a) - math.log10(b)) < 3 * rel_tol
            else:
                # Fall back to sign comparison for mixed signs
                return math.copysign(1, a) == math.copysign(1, b) and abs(a - b) < abs_tol * max(abs(a), abs(b))
        
        # Handle very small numbers (near zero)
        if abs(a) < 1e-100 and abs(b) < 1e-100:
            # For very small numbers, use absolute tolerance only
            return abs(a - b) < abs_tol
        
        return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
    
    # Handle mixed numeric types (int and float)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        # Check for potential precision loss in large integers
        if isinstance(a, int) and abs(a) > 2**53:  # JavaScript safe integer limit
            logger.debug(f"Large integer comparison: {a} may lose precision in JSON serialization")
        if isinstance(b, int) and abs(b) > 2**53:
            logger.debug(f"Large integer comparison: {b} may lose precision in JSON serialization")
        
        return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)
    
    # Handle complex numbers
    if isinstance(a, complex) and isinstance(b, complex):
        # Compare real and imaginary parts separately
        real_equal = math.isclose(a.real, b.real, rel_tol=rel_tol, abs_tol=abs_tol)
        imag_equal = math.isclose(a.imag, b.imag, rel_tol=rel_tol, abs_tol=abs_tol)
        return real_equal and imag_equal
    
    # Handle Decimal type (if available)
    try:
        from decimal import Decimal
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            # Convert to float for comparison
            a_float = float(a) if isinstance(a, Decimal) else a
            b_float = float(b) if isinstance(b, Decimal) else b
            if isinstance(a_float, (int, float)) and isinstance(b_float, (int, float)):
                return math.isclose(a_float, b_float, rel_tol=rel_tol, abs_tol=abs_tol)
    except ImportError:
        pass
    
    # NumPy array handling
    if HAS_NUMPY and np is not None:
        # Check if either is a numpy array
        a_is_array = isinstance(a, np.ndarray)
        b_is_array = isinstance(b, np.ndarray)
        
        if a_is_array or b_is_array:
            try:
                # Only compare if both are numpy arrays (no automatic conversion)
                if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
                    # Check shapes
                    if a.shape != b.shape:
                        return False
                    # Use numpy's allclose with equal_nan=True
                    return np.allclose(a, b, rtol=rel_tol, atol=abs_tol, equal_nan=True)
                else:
                    # Type mismatch: one is array, other is not
                    return False
            except Exception as e:
                logger.debug(f"NumPy comparison failed: {e}")
                return False
    
    # Pandas DataFrame/Series handling
    if HAS_PANDAS and pd is not None and pd_testing is not None:
        # Check for pandas DataFrame
        if hasattr(pd, 'DataFrame') and isinstance(a, pd.DataFrame) and isinstance(b, pd.DataFrame):
            try:
                pd_testing.assert_frame_equal(
                    a, b, 
                    check_exact=False,
                    rtol=rel_tol,
                    atol=abs_tol,
                    check_dtype=False,
                    check_categorical=False
                )
                return True
            except AssertionError:
                return False
            except Exception as e:
                logger.debug(f"Pandas DataFrame comparison failed: {e}")
                return False
        
        # Check for pandas Series
        if hasattr(pd, 'Series') and isinstance(a, pd.Series) and isinstance(b, pd.Series):
            try:
                pd_testing.assert_series_equal(
                    a, b,
                    check_exact=False,
                    rtol=rel_tol,
                    atol=abs_tol,
                    check_dtype=False,
                    check_categorical=False
                )
                return True
            except AssertionError:
                return False
            except Exception as e:
                logger.debug(f"Pandas Series comparison failed: {e}")
                return False
    
    # Basic types
    if isinstance(a, (int, str, bool, type(None))) and isinstance(b, (int, str, bool, type(None))):
        return a == b
    
    # Container types with circular reference protection
    if isinstance(a, (list, tuple, set, dict)):
        # Create unique identifiers for containers to detect circular references
        # Using object IDs to identify specific container instances
        id_a, id_b = id(a), id(b)
        # Create a canonical key (smaller id first) to ensure consistent checking
        # regardless of argument order (deep_equal(a,b) == deep_equal(b,a))
        key = (id_a, id_b) if id_a < id_b else (id_b, id_a)
        
        if key in _visited:
            # Already comparing these objects - assume equal to break cycle
            # This prevents infinite recursion in circular structures like:
            # a = [1, 2]; a.append(a)  # a contains itself
            return True
        
        # Mark this pair as being compared to detect future circular references
        _visited.add(key)
        
        try:
            if isinstance(a, list) and isinstance(b, list):
                if len(a) != len(b):
                    return False
                return all(deep_equal(x, y, rel_tol, abs_tol, _visited, _depth + 1) 
                          for x, y in zip(a, b))
            
            elif isinstance(a, tuple) and isinstance(b, tuple):
                if len(a) != len(b):
                    return False
                return all(deep_equal(x, y, rel_tol, abs_tol, _visited, _depth + 1) 
                          for x, y in zip(a, b))
            
            elif isinstance(a, set) and isinstance(b, set):
                if len(a) != len(b):
                    return False
                # For sets, need to find matching elements
                b_copy = b.copy()
                for elem_a in a:
                    found = False
                    for elem_b in b_copy:
                        if deep_equal(elem_a, elem_b, rel_tol, abs_tol, _visited, _depth + 1):
                            b_copy.remove(elem_b)
                            found = True
                            break
                    if not found:
                        return False
                return True
            
            elif isinstance(a, dict) and isinstance(b, dict):
                if a.keys() != b.keys():
                    return False
                return all(deep_equal(a[k], b[k], rel_tol, abs_tol, _visited, _depth + 1) 
                          for k in a)
        finally:
            _visited.discard(key)
    
    # Fallback: try direct comparison
    try:
        return a == b
    except Exception as e:
        logger.debug(f"Direct comparison failed for types {type(a)} and {type(b)}: {e}")
        return False


def deep_equal_simple(a: Any, b: Any, rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> bool:
    """
    Simplified deep equal for sandbox comparison with float tolerance.
    
    This is a minimal version suitable for use in sandboxed environments
    where external dependencies may not be available.
    
    Args:
        a, b: Objects to compare
        rel_tol: Relative tolerance for floating-point comparisons
        abs_tol: Absolute tolerance for floating-point comparisons
        
    Returns:
        bool: True if objects are equal within tolerance, False otherwise
    """
    # Handle float comparisons
    if isinstance(a, float) and isinstance(b, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
    
    # Handle mixed numeric types
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)
    
    # Handle lists
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(deep_equal_simple(x, y, rel_tol, abs_tol) for x, y in zip(a, b))
    
    # Handle dicts
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(deep_equal_simple(a[k], b[k], rel_tol, abs_tol) for k in a)
    
    # Fallback to regular comparison
    return a == b