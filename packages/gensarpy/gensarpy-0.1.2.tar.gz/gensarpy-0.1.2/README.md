# gensarpy

A Python library for testing the convergence of mathematical series.

## Installation

```bash
pip install gensarpy
```

## Usage

```python
from gensarpy.convergence_tests import check_convergence

# Test a convergent series
result = check_convergence('1/n**2')
print(result)  # Output: Convergent by the P-Series Test

# Test a divergent series
result = check_convergence('1/n')
print(result)  # Output: Divergent by the P-Series Test
```
