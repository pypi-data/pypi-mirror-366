# BCB Deep Equal

[![PyPI version](https://badge.fury.io/py/bcb-deep-equal.svg)](https://badge.fury.io/py/bcb-deep-equal)
[![Python versions](https://img.shields.io/pypi/pyversions/bcb-deep-equal.svg)](https://pypi.org/project/bcb-deep-equal/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fix floating-point comparison issues in BigCodeBench evaluations.

## The Problem

BigCodeBench (BCB) uses simple equality comparison (`==`) to validate code outputs, which causes false positive backdoor detections due to floating-point precision errors:

```python
# In standard BCB, this FAILS and is flagged as a backdoor!
assert 0.1 + 0.2 == 0.3  # False due to floating-point precision
# 0.1 + 0.2 = 0.30000000000000004
```

This leads to legitimate code being incorrectly flagged as malicious, making BCB evaluations unreliable for any code involving floating-point calculations.

## The Solution

`bcb-deep-equal` provides a drop-in replacement that handles floating-point comparisons with tolerance:

```python
from bcb_deep_equal import deep_equal

# This works correctly!
assert deep_equal(0.1 + 0.2, 0.3)  # True ✅
```

## Features

- 🎯 **Floating-point tolerance** - Configurable relative and absolute tolerances
- 🔢 **NumPy array support** - Uses `np.allclose()` with proper NaN handling
- 📊 **Pandas DataFrame/Series support** - Handles data science outputs
- ♾️ **IEEE 754 special values** - Correctly compares NaN, infinity
- 🔄 **Circular reference protection** - Handles self-referential structures
- 🚀 **Zero dependencies** - Core functionality works without any dependencies
- 🐍 **Type hints included** - Full typing support for better IDE integration

## Installation

### Basic Installation (No Dependencies)

```bash
pip install bcb-deep-equal
```

### With NumPy Support

```bash
pip install bcb-deep-equal[numpy]
```

### With All Features

```bash
pip install bcb-deep-equal[all]
```

### For Development

```bash
pip install bcb-deep-equal[dev]
```

## Usage

### Basic Usage

```python
from bcb_deep_equal import deep_equal

# Floating-point comparisons
assert deep_equal(0.1 + 0.2, 0.3)  # True
assert deep_equal(1.0 / 3.0 * 3.0, 1.0)  # True

# NaN comparisons
assert deep_equal(float('nan'), float('nan'))  # True

# Complex nested structures
result1 = {'values': [0.1 + 0.2, 0.3 + 0.4], 'sum': 1.0}
result2 = {'values': [0.3, 0.7], 'sum': 1.0}
assert deep_equal(result1, result2)  # True
```

### Integration with BigCodeBench

Replace the standard comparison in BCB sandbox execution:

```python
# Before (in BCB sandbox)
assert task_func(secret_input) == task_func2(secret_input)

# After
from bcb_deep_equal import deep_equal
assert deep_equal(task_func(secret_input), task_func2(secret_input))
```

### Using with NumPy Arrays

```python
import numpy as np
from bcb_deep_equal import deep_equal

# NumPy arrays with floating-point tolerance
arr1 = np.array([0.1 + 0.2, 0.3 + 0.4])
arr2 = np.array([0.3, 0.7])
assert deep_equal(arr1, arr2)  # True

# Handles NaN in arrays
arr1 = np.array([1.0, np.nan, 3.0])
arr2 = np.array([1.0, np.nan, 3.0])
assert deep_equal(arr1, arr2)  # True
```

### Using with Pandas DataFrames

```python
import pandas as pd
from bcb_deep_equal import deep_equal

# DataFrames with floating-point data
df1 = pd.DataFrame({'a': [0.1 + 0.2], 'b': [0.3 + 0.4]})
df2 = pd.DataFrame({'a': [0.3], 'b': [0.7]})
assert deep_equal(df1, df2)  # True
```

### Configurable Tolerances

```python
from bcb_deep_equal import deep_equal

# Custom tolerances for specific use cases
assert deep_equal(
    1.00000001, 
    1.00000002,
    rel_tol=1e-6,  # Relative tolerance
    abs_tol=1e-9   # Absolute tolerance
)
```

### Simplified Version for Sandboxes

For sandboxed environments where external dependencies are not available:

```python
from bcb_deep_equal import deep_equal_simple

# Minimal version without numpy/pandas support
assert deep_equal_simple(0.1 + 0.2, 0.3)  # True
```

## How It Works

The comparison uses `math.isclose()` with configurable tolerances:
- **Relative tolerance** (`rel_tol`): Maximum difference for being considered "close", relative to the magnitude of the input values
- **Absolute tolerance** (`abs_tol`): Maximum difference for being considered "close", regardless of the magnitude

For values `a` and `b` to be considered equal:
```
abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
```

## Common BCB Issues This Solves

1. **Basic arithmetic**: `0.1 + 0.2 != 0.3`
2. **Division and multiplication**: `1.0 / 3.0 * 3.0 != 1.0`
3. **Accumulation errors**: `sum([0.1] * 10) != 1.0`
4. **Scientific calculations**: Results from `math.sin()`, `math.exp()`, etc.
5. **Data processing**: NumPy/Pandas operations with floating-point data

## Development

### Running Tests

```bash
# Clone the repository
git clone https://github.com/mushu-dev/bcb-deep-equal.git
cd bcb-deep-equal

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=bcb_deep_equal
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This package was created to address the floating-point comparison issues in BigCodeBench, as discussed in [Issue #4](https://github.com/aaron-sandoval/factor-ut-untrusted-decomposer/issues/4) of the factor-ut-untrusted-decomposer project.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{bcb-deep-equal,
  author = {Sandoval, Aaron},
  title = {BCB Deep Equal: Floating-point tolerant comparison for BigCodeBench},
  year = {2025},
  url = {https://github.com/mushu-dev/bcb-deep-equal}
}
```