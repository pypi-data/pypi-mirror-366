"""
Biox SDK - EEG Data Processing and Visualization

This package provides tools for EEG data collection, processing, and visualization.
"""

# Import main modules for easy access
from . import ble
from . import collector
from . import command
from . import data
from . import util
from . import visualization

# Import commonly used classes
from .visualization import RealtimePlotter

__version__ = "1.0.0"
__all__ = [
    'ble', 'collector', 'command', 'data', 'util', 'visualization',
    'RealtimePlotter'
]