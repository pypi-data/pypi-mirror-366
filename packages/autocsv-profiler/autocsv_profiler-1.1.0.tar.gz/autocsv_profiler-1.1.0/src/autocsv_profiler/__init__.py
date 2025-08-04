"""
AutoCSV Profiler - Comprehensive automated CSV data analysis

A toolkit for automated CSV data analysis providing statistical insights,
data quality assessment, and interactive visualizations.
"""

__version__ = "1.1.0"
__author__ = "dhaneshbb"
__email__ = "dhaneshbb5@gmail.com"
__license__ = "MIT"

# Import main functions for easy access
try:
    from .auto_csv_profiler import main as analyze_csv
    from .recognize_delimiter import detect_delimiter
except ImportError:
    # Fallback if imports fail during development
    analyze_csv = None
    detect_delimiter = None

# Define what gets imported with "from autocsv_profiler import *"
__all__ = [
    "analyze_csv",
    "detect_delimiter",
    "__version__"
]

# Package metadata
__package_name__ = "autocsv-profiler"
__description__ = "Comprehensive automated CSV data analysis with statistical insights and visualizations"
__url__ = "https://github.com/dhaneshbb/AutoCSV-Profiler-Suite"