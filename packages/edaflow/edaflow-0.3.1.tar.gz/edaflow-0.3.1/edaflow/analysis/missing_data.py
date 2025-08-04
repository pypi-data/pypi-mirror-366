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


def visualize_categorical_values(df: pd.DataFrame, 
                                max_unique_values: Optional[int] = 20,
                                show_counts: bool = True,
                                show_percentages: bool = True) -> None:
    """
    Visualize unique values in categorical (object-type) columns with counts and percentages.
    
    This function provides a comprehensive overview of categorical columns by displaying:
    - Unique values in each categorical column
    - Value counts (frequency of each unique value)
    - Percentages (relative frequency)
    - Summary statistics for each column
    
    Args:
        df (pd.DataFrame): The input DataFrame to analyze
        max_unique_values (Optional[int], optional): Maximum number of unique values 
                                                   to display per column. If a column 
                                                   has more unique values, only the top 
                                                   N most frequent will be shown. 
                                                   Defaults to 20.
        show_counts (bool, optional): Whether to show the count of each unique value.
                                    Defaults to True.
        show_percentages (bool, optional): Whether to show the percentage of each 
                                         unique value. Defaults to True.
    
    Returns:
        None: Prints visualization results directly to console with formatting
    
    Example:
        >>> import pandas as pd
        >>> import edaflow
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'B', 'A', 'C', 'B', 'A'],
        ...     'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        ...     'region': ['North', 'South', 'North', 'East', 'West', 'North'],
        ...     'score': [85, 92, 78, 88, 95, 82]
        ... })
        >>> 
        >>> # Basic visualization
        >>> edaflow.visualize_categorical_values(df)
        >>> 
        >>> # Show only top 10 values per column, without percentages
        >>> edaflow.visualize_categorical_values(df, max_unique_values=10, show_percentages=False)
        >>> 
        >>> # Alternative import style:
        >>> from edaflow.analysis import visualize_categorical_values
        >>> visualize_categorical_values(df, max_unique_values=15)
    
    Notes:
        - Only analyzes columns with object dtype (categorical/string columns)
        - Columns with many unique values are truncated to show most frequent ones
        - Provides summary statistics including total unique values and most common value
        - Uses color coding to highlight column names and important information
    """
    # Find categorical columns
    cat_columns = [col for col in df.columns if df[col].dtype == 'object']
    
    if not cat_columns:
        print("🔍 No categorical (object-type) columns found in the DataFrame.")
        print("   All columns appear to be numeric or datetime types.")
        return
    
    print("📊 CATEGORICAL COLUMNS VISUALIZATION")
    print("=" * 70)
    print(f"Found {len(cat_columns)} categorical column(s): {', '.join(cat_columns)}")
    print("=" * 70)
    
    for i, col in enumerate(cat_columns, 1):
        # Get value counts
        value_counts = df[col].value_counts(dropna=False)
        total_values = len(df[col])
        unique_count = len(value_counts)
        
        # Handle missing values
        null_count = df[col].isnull().sum()
        
        # Column header with color coding
        print(f'\n\x1b[1;36m[{i}/{len(cat_columns)}] Column: {col}\x1b[m')
        print(f'📈 Total values: {total_values} | Unique values: {unique_count} | Missing: {null_count}')
        
        if unique_count == 0:
            print('⚠️  Column is completely empty')
            continue
            
        # Determine how many values to show
        values_to_show = min(max_unique_values, unique_count)
        
        if unique_count > max_unique_values:
            print(f'📋 Showing top {values_to_show} most frequent values (out of {unique_count} total):')
        else:
            print(f'📋 All unique values:')
        
        # Display values with counts and percentages
        for j, (value, count) in enumerate(value_counts.head(values_to_show).items(), 1):
            # Handle NaN values display
            display_value = 'NaN/Missing' if pd.isna(value) else repr(value)
            
            # Calculate percentage
            percentage = (count / total_values) * 100
            
            # Build the display string
            display_parts = [f'   {j:2d}. {display_value}']
            
            if show_counts:
                display_parts.append(f'Count: {count}')
            
            if show_percentages:
                display_parts.append(f'({percentage:.1f}%)')
            
            print(' | '.join(display_parts))
        
        # Show truncation message if needed
        if unique_count > max_unique_values:
            remaining = unique_count - max_unique_values
            print(f'   ... and {remaining} more unique value(s)')
        
        # Summary statistics
        most_common_value = value_counts.index[0]
        most_common_count = value_counts.iloc[0]
        most_common_pct = (most_common_count / total_values) * 100
        
        display_most_common = 'NaN/Missing' if pd.isna(most_common_value) else repr(most_common_value)
        
        print(f'🏆 Most frequent: {display_most_common} ({most_common_count} times, {most_common_pct:.1f}%)')
        
        # Add separator between columns (except for the last one)
        if i < len(cat_columns):
            print('-' * 50)
    
    print("\n" + "=" * 70)
    print("✅ Categorical visualization complete!")
    
    # Provide actionable insights
    high_cardinality_cols = [col for col in cat_columns if df[col].nunique() > max_unique_values]
    if high_cardinality_cols:
        print(f"\n💡 High cardinality columns detected: {', '.join(high_cardinality_cols)}")
        print("   Consider: grouping rare categories, encoding, or feature engineering")
    
    # Check for columns that might need attention
    mostly_unique_cols = [col for col in cat_columns if df[col].nunique() / len(df) > 0.8]
    if mostly_unique_cols:
        print(f"\n⚠️  Mostly unique columns (>80% unique): {', '.join(mostly_unique_cols)}")
        print("   These might be IDs or need special handling")


def display_column_types(df):
    """
    Display categorical and numerical columns in a DataFrame.
    
    This function separates DataFrame columns into categorical (object dtype) 
    and numerical (non-object dtypes) columns and displays them in a clear format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to analyze
        
    Returns:
    --------
    dict
        Dictionary containing 'categorical' and 'numerical' lists of column names
        
    Example:
    --------
    >>> import pandas as pd
    >>> from edaflow import display_column_types
    >>> 
    >>> # Create sample data
    >>> data = {
    ...     'name': ['Alice', 'Bob', 'Charlie'],
    ...     'age': [25, 30, 35],
    ...     'city': ['NYC', 'LA', 'Chicago'],
    ...     'salary': [50000, 60000, 70000],
    ...     'is_active': [True, False, True]
    ... }
    >>> df = pd.DataFrame(data)
    >>> 
    >>> # Display column types
    >>> result = display_column_types(df)
    >>> print("Categorical columns:", result['categorical'])
    >>> print("Numerical columns:", result['numerical'])
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    if df.empty:
        print("⚠️  DataFrame is empty!")
        return {'categorical': [], 'numerical': []}
    
    # Separate columns by type
    cat_cols = [col for col in df.columns if df[col].dtype == 'object']
    num_cols = [col for col in df.columns if df[col].dtype != 'object']
    
    # Display results
    print("📊 Column Type Analysis")
    print("=" * 50)
    
    print(f"\n📝 Categorical Columns ({len(cat_cols)} total):")
    if cat_cols:
        for i, col in enumerate(cat_cols, 1):
            unique_count = df[col].nunique()
            print(f"   {i:2d}. {col:<20} (unique values: {unique_count})")
    else:
        print("   No categorical columns found")
    
    print(f"\n🔢 Numerical Columns ({len(num_cols)} total):")
    if num_cols:
        for i, col in enumerate(num_cols, 1):
            dtype = str(df[col].dtype)
            print(f"   {i:2d}. {col:<20} (dtype: {dtype})")
    else:
        print("   No numerical columns found")
    
    # Summary
    total_cols = len(df.columns)
    cat_percentage = (len(cat_cols) / total_cols * 100) if total_cols > 0 else 0
    num_percentage = (len(num_cols) / total_cols * 100) if total_cols > 0 else 0
    
    print(f"\n📈 Summary:")
    print(f"   Total columns: {total_cols}")
    print(f"   Categorical: {len(cat_cols)} ({cat_percentage:.1f}%)")
    print(f"   Numerical: {len(num_cols)} ({num_percentage:.1f}%)")
    
    return {
        'categorical': cat_cols,
        'numerical': num_cols
    }
