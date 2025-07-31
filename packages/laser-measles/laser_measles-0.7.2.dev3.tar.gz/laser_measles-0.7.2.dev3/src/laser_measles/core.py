"""
Core computational functions for laser-measles.

This module provides core computational utilities, with optional
compiled extensions for performance optimization.
"""

try:
    from ._core import compute
except ImportError:

    def compute(args):
        return max(args, key=len)


__all__ = [
    "compute",
]
