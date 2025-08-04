"""
Configuration constants for BCB comparison.
"""

# Default tolerance values based on research and empirical testing
BCB_COMPARISON_CONFIG = {
    "rel_tol": 1e-6,  # Relative tolerance for floating-point comparisons
    "abs_tol": 1e-9,  # Absolute tolerance for floating-point comparisons
    "max_recursion_depth": 100,  # Maximum recursion depth for nested structures
}

# Common floating-point edge cases in BigCodeBench
COMMON_BCB_FLOAT_ISSUES = [
    (0.1 + 0.2, 0.3),  # Classic example: 0.30000000000000004 != 0.3
    (1.0 / 3.0 * 3.0, 1.0),  # Rounding after division
    (0.1 * 10, 1.0),  # Accumulation errors
]