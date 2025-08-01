"""
lillib - A small collection of utility functions.
"""

__version__ = "0.2.0"
__author__ = "Lilly"
__email__ = "ghostoverflow256@gmail.com"

# Import everything from units module - any new functions you add there
# will automatically be available when importing lillib
from .units import *
from .json_filetree import *

# Define which functions are exposed when using 'from lillib import *'
# This should match the functions available in units.py
__all__ = ["humanbytes", "json_filetree"]
