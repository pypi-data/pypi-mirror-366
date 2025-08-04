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


def convert_to_numeric(df: pd.DataFrame, 
                      threshold: Optional[float] = 35,
                      inplace: bool = False) -> pd.DataFrame:
    """
    Convert object columns to numeric when appropriate based on data analysis.
    
    This function examines object-type columns and converts them to numeric
    if the percentage of non-numeric values is below the specified threshold.
    This helps clean datasets where numeric data is stored as strings.
    
    Args:
        df (pd.DataFrame): The input DataFrame to process
        threshold (Optional[float], optional): The threshold percentage for 
                                             non-numeric values. Columns with
                                             fewer non-numeric values than this
                                             threshold will be converted to numeric.
                                             Defaults to 35.
        inplace (bool, optional): If True, modify the DataFrame in place and return None.
                                If False, return a new DataFrame with conversions applied.
                                Defaults to False.
    
    Returns:
        pd.DataFrame or None: If inplace=False, returns a new DataFrame with 
                            numeric conversions applied. If inplace=True, 
                            modifies the original DataFrame and returns None.
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'name': ['Alice', 'Bob', 'Charlie'],
        ...     'age_str': ['25', '30', '35'], 
        ...     'mixed': ['1', '2', 'three'],
        ...     'numbers': [1, 2, 3]
        ... })
        >>> 
        >>> # Create a copy with conversions
        >>> df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
        >>> 
        >>> # Or modify the original DataFrame
        >>> edaflow.convert_to_numeric(df, threshold=35, inplace=True)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import convert_to_numeric
        >>> df_cleaned = convert_to_numeric(df, threshold=50)
    
    Notes:
        - Values that cannot be converted to numeric become NaN
        - The function provides colored output showing which columns were converted
        - Use a lower threshold to be more strict about conversions
        - Use a higher threshold to be more lenient about mixed data
    """
    # Create a copy if not modifying inplace
    if not inplace:
        df_result = df.copy()
    else:
        df_result = df
    
    print("Converting object columns to numeric where appropriate...")
    print("=" * 60)
    
    conversions_made = []
    
    for col in df_result.columns:
        if df_result[col].dtype == 'object':
            # Try to convert to numeric and check how many fail
            numeric_col = pd.to_numeric(df_result[col], errors='coerce')
            non_numeric_pct = (numeric_col.isnull().sum() / len(numeric_col)) * 100
            
            if non_numeric_pct < threshold:
                # Convert the column to numeric
                original_nulls = df_result[col].isnull().sum()
                df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
                new_nulls = df_result[col].isnull().sum()
                values_converted_to_nan = new_nulls - original_nulls
                
                # Colored output for successful conversion
                print('\x1b[1;31;44mConverting {} to a numerical column\x1b[m'.format(col))
                print('  └─ {}% of values were non-numeric ({} values converted to NaN)'.format(
                    round(non_numeric_pct, 2), values_converted_to_nan
                ))
                
                conversions_made.append({
                    'column': col,
                    'non_numeric_pct': round(non_numeric_pct, 2),
                    'values_converted_to_nan': values_converted_to_nan
                })
            else:
                # Skip conversion - too many non-numeric values
                print('{} skipped: {}% non-numeric values (threshold: {}%)'.format(
                    col, round(non_numeric_pct, 2), threshold
                ))
        else:
            print('{} skipped: already numeric (dtype: {})'.format(col, df_result[col].dtype))
    
    print("=" * 60)
    
    if conversions_made:
        print(f"✅ Successfully converted {len(conversions_made)} columns to numeric:")
        for conversion in conversions_made:
            print(f"   • {conversion['column']}: {conversion['non_numeric_pct']}% non-numeric")
    else:
        print("ℹ️  No columns were converted (all were either already numeric or above threshold)")
    
    print("Conversion complete!")
    
    # Return the result DataFrame if not inplace, otherwise return None
    return None if inplace else df_result
