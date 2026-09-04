"""
hmaraniam - High-precision language identification for Hmar.
"Hmar a ni am?" -> "Is it Hmar?"

Pure string language identification engine.
"""

from hmaraniam.detector import Detector, detect, get_default_detector

__version__ = "0.1.1"
__author__ = "Hmar Heritage Project"
__license__ = "MIT"

__all__ = [
    "Detector",
    "detect",
    "get_default_detector",
    "__version__",
]
