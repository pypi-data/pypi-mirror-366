# SimaiParser/__init__.py

"""
Simai Parser Package
--------------------

This package provides tools to parse Simai chart files into a structured
JSON format.
"""

from .core import SimaiChart
from .slide_calc import SimaiSlideCalculator

__all__ = ['SimaiChart']

__version__ = "0.2.1"
