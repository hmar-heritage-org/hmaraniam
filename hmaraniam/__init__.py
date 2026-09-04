"""
hmaraniam - High-precision language identification for Hmar.
"Hmar a ni am?" -> "Is it Hmar?"
"""

from hmaraniam.detector import (
    Detector,
    acp_pradyuman,
    detect,
    detect_file,
    detect_html,
    get_default_detector,
)

__version__ = "0.1.0"
__author__ = "Hmar Heritage Project"
__license__ = "MIT"

__all__ = [
    "Detector",
    "detect",
    "detect_file",
    "detect_html",
    "acp_pradyuman",
    "get_default_detector",
    "__version__",
]
