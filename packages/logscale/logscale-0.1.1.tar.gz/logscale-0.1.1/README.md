# logscale

This Python package provides a single function, `order_of_magnitude()`, which computes and returns the order of magnitude of a given number in a standardized string format.

The order of magnitude gives a compact representation of a number as a product of a coefficient and a power of 10, where the coefficient is constrained to lie within the interval [1/√10, √10). For more information, see the [wikipedia article](https://en.wikipedia.org/wiki/Order_of_magnitude) on orders of magnitude.

## Installation

If you are using `uv`, you can install the package from PyPI with:

    uv pip install logscale

Alternatively, with regular `pip`:

    pip install logscale

## Examples

```python
from logscale import order_of_magnitude

order_of_magnitude(129)  # "1.3e2"
order_of_magnitude(0.0001)  # "1.0e-4"
order_of_magnitude(456)  # "0.46e3"
order_of_magnitude(70.2)  # "0.70e2"
order_of_magnitude(0)  # "0.0e0"
```
