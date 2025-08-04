"""
BCB Deep Equal - Floating-point tolerant comparison for BigCodeBench.

This package provides a solution to the floating-point comparison issues
in BigCodeBench that cause false positive backdoor detections.

Example:
    >>> from bcb_deep_equal import deep_equal
    >>> deep_equal(0.1 + 0.2, 0.3)  # Returns True
    True
"""

from .deep_equal import deep_equal, deep_equal_simple
from .constants import BCB_COMPARISON_CONFIG

__version__ = "0.1.0"
__all__ = ["deep_equal", "deep_equal_simple", "BCB_COMPARISON_CONFIG"]

# Convenience function for BCB integration
def patch_bcb_comparison():
    """
    Monkey-patch BCB's comparison to use deep_equal.
    
    This is a convenience function for users who want to quickly
    fix their existing BCB installation without modifying code.
    
    Note: This should be called before importing BCB modules.
    """
    import warnings
    warnings.warn(
        "patch_bcb_comparison is experimental. "
        "Consider modifying BCB code directly for production use.",
        UserWarning
    )