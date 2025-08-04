"""
Missing data analysis functions for edaflow.

This module provides utilities for analyzing and visualizing missing data patterns.
"""

import pandas as pd
from typing import Optional


def check_null_columns(df: pd.DataFrame,
                       threshold: Optional[float] = 10) -> pd.DataFrame:
    """
    Check null values in DataFrame columns with styled output.

    Calculates the percentage of null values per column and applies color styling
    based on the percentage of nulls relative to the threshold.

    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for
                                             highlighting. Defaults to 10.

    Returns:
        pd.DataFrame: A styled DataFrame showing column names and null
                     percentages with color coding:
                     - Red: > 2*threshold (high null percentage)
                     - Yellow: > threshold but <= 2*threshold (medium null %)
                     - Light yellow: > 0 but <= threshold (low null %)
                     - Gray: 0 (no nulls)

    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({'A': [1, 2, None], 'B': [1, None, None]})
        >>> styled_result = edaflow.check_null_columns(df, threshold=20)
        >>> # Returns styled DataFrame with null percentages

        # Alternative import style:
        >>> from edaflow.analysis import check_null_columns
        >>> styled_result = check_null_columns(df, threshold=20)
    """
    # Calculate null percentages
    null_counts = df.isnull().sum()
    total_rows = len(df)
    null_percentages = (null_counts / total_rows * 100).round(2)

    # Create result DataFrame
    result_df = pd.DataFrame({
        'Column': df.columns,
        'Null_Count': null_counts.values,
        'Null_Percentage': null_percentages.values
    })

    def style_nulls(val):
        """Apply color styling based on null percentage."""
        if val == 0:
            return 'background-color: lightgray'
        elif val > threshold * 2:
            return 'background-color: red; color: white'
        elif val > threshold:
            return 'background-color: yellow'
        else:  # val > 0
            return 'background-color: lightyellow'

    # Apply styling to the Null_Percentage column
    styled_df = result_df.style.map(style_nulls, subset=['Null_Percentage'])

    return styled_df


def analyze_categorical_columns(df: pd.DataFrame, 
                              threshold: Optional[float] = 35) -> None:
    """
    Analyze categorical columns of object type to identify potential data issues.
    
    This function examines object-type columns to detect:
    1. Columns that might be numeric but stored as strings
    2. Categorical columns with their unique values
    3. Data type consistency issues
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. If a column 
                                             has less than this percentage of 
                                             non-numeric values, it's flagged 
                                             as potentially numeric. Defaults to 35.
    
    Returns:
        None: Prints analysis results directly to console with color coding
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> edaflow.analyze_categorical_columns(df, threshold=35)
        # Output with color coding:
        # age_str is potentially a numeric column that needs conversion
        # age_str has ['25' '30' '35'] values
        # mixed has too many non-numeric values (33.33% non-numeric)
        # numbers is not an object column
        
        # Alternative import style:
        >>> from edaflow.analysis import analyze_categorical_columns
    """
    print("Analyzing categorical columns of object type...")
    print("=" * 50)
    
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to numeric and check how many fail
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
            
            if non_numeric_pct < threshold:
                # Potential numeric column - highlight in red with blue background
                print('\x1b[1;31;44m{} is potentially a numeric column that needs conversion\x1b[m'.format(col))
                print('\x1b[1;30;43m{} has {} unique values: {}\x1b[m'.format(
                    col, df[col].nunique(), df[col].unique()[:10]  # Show first 10 unique values
                ))
            else:
                # Truly categorical column
                unique_count = df[col].nunique()
                total_count = len(df[col])
                print('{} has too many non-numeric values ({}% non-numeric)'.format(
                    col, round(non_numeric_pct, 2)
                ))
                print('  └─ {} unique values out of {} total ({} unique values shown): {}'.format(
                    unique_count, total_count, min(10, unique_count), 
                    df[col].unique()[:10]  # Show first 10 unique values
                ))
        else:
            print('{} is not an object column (dtype: {})'.format(col, df[col].dtype))
    
    print("=" * 50)
    print("Analysis complete!")
