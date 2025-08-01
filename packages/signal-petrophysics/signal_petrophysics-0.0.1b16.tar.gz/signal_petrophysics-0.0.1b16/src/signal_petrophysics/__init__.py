"""Signal Petrophysics Package

A comprehensive library for handling reading, analysing and plotting 
Well-Log Pattern Recognition algorithms from Signal-Processing.
"""

from . import load_data
from . import pattern_find
from . import plot
from . import postprocessing
from . import signal_adapt
from . import utils

__version__ = "0.0.1b15"
__author__ = "Maria Fernanda Gonzalez"
__email__ = "mariafgg@utexas.edu"

__all__ = [
    "load_data",
    "pattern_find", 
    "plot",
    "postprocessing",
    "signal_adapt",
    "utils",
]
