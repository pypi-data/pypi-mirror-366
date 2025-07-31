"""
The Youtube Autonomous Testing Module.
"""
import pytest


def float_approx_to_compare(float):
    """
    Compare float values with 
    approximation due to the decimal
    differences we can have.

    Then, you can compare floats by
    using:

    - `assert fa == float_approx_to_compare(fb)`
    """
    return pytest.approx(float, rel = 1e-5, abs = 1e-8)