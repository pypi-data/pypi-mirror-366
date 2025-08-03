"""Module defining a function to compute the order of magnitude of a number."""

import math


def order_of_magnitude(x: float) -> str:
    """Return a string representing the order of magnitude of a number.

    The order of magnitude is the exponent of 10 such that the coefficient (mantissa)
    is between 1/sqrt(10) and sqrt(10).
    The result is formatted as '<coefficient>e<exponent>',
    with the coefficient rounded to two significant digits.
    """
    if x == 0.0:
        return "0.0e0"

    sign = -1 if x < 0.0 else 1

    x = abs(x)

    exponent = math.floor(math.log10(x) + 0.5)

    coefficient = x / (10**exponent)

    # Ensure two significant digits
    if float(f"{coefficient:.1f}") >= 1:
        return f"{sign * coefficient:.1f}e{exponent}"
    return f"{sign * coefficient:.2f}e{exponent}"
