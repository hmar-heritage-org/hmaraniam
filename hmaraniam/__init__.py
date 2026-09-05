"""
hmaraniam - Language identification library for Hmar.
"Hmar a ni am?" -> "Is it Hmar?"

Pure string language identification engine.
"""

from hmaraniam.detector import Detector, detect, get_default_detector

__version__ = "0.1.4"
__author__ = "Hmar Heritage Foundation"
__license__ = "MIT"

__all__ = [
    "Detector",
    "detect",
    "get_default_detector",
    "__version__",
]
