"""
edaflow - A Python package for exploratory data analysis workflows
"""

from .analysis import check_null_columns, analyze_categorical_columns

__version__ = "0.1.0"
__author__ = "Evan Low"
__email__ = "evan.low@illumetechnology.com"


def hello():
    """
    A sample hello function to test the package installation.

    Returns:
        str: A greeting message
    """
    return "Hello from edaflow! Ready for exploratory data analysis."


# Import main modules
# from .visualization import *
# from .preprocessing import *

# Export main functions
__all__ = ['hello', 'check_null_columns']
