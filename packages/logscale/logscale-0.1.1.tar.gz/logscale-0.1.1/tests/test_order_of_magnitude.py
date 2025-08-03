"""Tests for the order_of_magnitude function."""

from __future__ import annotations

import math

from logscale import order_of_magnitude


def test_order_of_magnitude_zero() -> None:
    """Test the order_of_magnitude function with zero."""
    assert order_of_magnitude(0) == "0.0e0"
    assert order_of_magnitude(-0) == "0.0e0"


def test_order_of_magnitude_positive() -> None:
    """Test the order_of_magnitude function with positive numbers."""
    assert order_of_magnitude(129) == "1.3e2"
    assert order_of_magnitude(0.121) == "1.2e-1"
    assert order_of_magnitude(0.0001) == "1.0e-4"
    assert order_of_magnitude(456) == "0.46e3"
    assert order_of_magnitude(0.451) == "0.45e0"
    assert order_of_magnitude(1) == "1.0e0"


def test_order_of_magnitude_negative() -> None:
    """Test the order_of_magnitude function with negative numbers."""
    assert order_of_magnitude(-129) == "-1.3e2"
    assert order_of_magnitude(-0.121) == "-1.2e-1"
    assert order_of_magnitude(-0.0001) == "-1.0e-4"
    assert order_of_magnitude(-456) == "-0.46e3"
    assert order_of_magnitude(-0.451) == "-0.45e0"
    assert order_of_magnitude(-1) == "-1.0e0"


def test_order_of_magnitude_edge_cases() -> None:
    """Test the order_of_magnitude function with edge cases."""
    x1 = math.sqrt(10) - 1e-9
    assert order_of_magnitude(x1) == "3.2e0"

    x2 = math.sqrt(10) + 1e-9
    assert order_of_magnitude(x2) == "0.32e1"

    x3 = math.sqrt(10)
    assert order_of_magnitude(x3) == "0.32e1"

    x4 = 1 / math.sqrt(10) - 1e-9
    assert order_of_magnitude(x4) == "3.2e-1"

    x5 = 1 / math.sqrt(10) + 1e-9
    assert order_of_magnitude(x5) == "0.32e0"

    x6 = 9.999999999999999999999999999999
    assert order_of_magnitude(x6) == "1.0e1"

    x7 = 9.9999999999
    assert order_of_magnitude(x7) == "1.0e1"
