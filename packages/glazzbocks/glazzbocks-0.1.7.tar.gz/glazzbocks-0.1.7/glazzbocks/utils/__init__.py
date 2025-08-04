"""
Utility modules for shared preprocessing, plotting, and formatting.
"""

from .preprocessing import create_numeric_pipeline, create_categorical_pipeline
from .plots import save_plot_to_base64, format_axes
from .formatting import format_number, truncate_dataframe

__all__ = [
    "create_numeric_pipeline",
    "create_categorical_pipeline",
    "save_plot_to_base64",
    "format_axes",
    "format_number",
    "truncate_dataframe",
]
