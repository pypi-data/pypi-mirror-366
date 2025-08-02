"""
Shaheenviz - Unified EDA Solution

Shaheenviz combines the analytical power of YData Profiling with the stunning 
visuals of Sweetviz to deliver a unified, automatic EDA solution.
"""

__version__ = "0.1.3"
__author__ = "Hamza"
__license__ = "MIT"

from .core import generate_report, quick_profile, compare_datasets, ShaheenvizReport
from .profiling_wrapper import ProfileWrapper
from .sweetviz_wrapper import SweetvizWrapper
from .utils import detect_target, save_reports

__all__ = [
    "generate_report",
    "quick_profile",
    "compare_datasets",
    "ShaheenvizReport", 
    "ProfileWrapper",
    "SweetvizWrapper",
    "detect_target",
    "save_reports",
]
