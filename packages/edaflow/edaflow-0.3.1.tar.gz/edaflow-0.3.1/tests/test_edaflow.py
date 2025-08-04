"""
Tests for the main edaflow module
"""
import pandas as pd
import edaflow
from edaflow.analysis import check_null_columns, analyze_categorical_columns, convert_to_numeric, visualize_categorical_values, display_column_types


def test_hello_function():
    """Test the hello function returns expected message"""
    result = edaflow.hello()
    assert isinstance(result, str)
    assert "Hello from edaflow" in result
    assert "exploratory data analysis" in result


def test_version_exists():
    """Test that version is defined"""
    assert hasattr(edaflow, '__version__')
    assert isinstance(edaflow.__version__, str)


def test_author_exists():
    """Test that author information is defined"""
    assert hasattr(edaflow, '__author__')
    assert isinstance(edaflow.__author__, str)


def test_email_exists():
    """Test that email information is defined"""
    assert hasattr(edaflow, '__email__')
    assert isinstance(edaflow.__email__, str)


def test_check_null_columns_import_from_main():
    """Test check_null_columns imported from main edaflow module"""
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],  # No nulls
        'B': [1, 2, None, 4, 5],  # 20% nulls
    })
    
    result = edaflow.check_null_columns(df, threshold=10)
    
    # Check that result is a styled DataFrame
    assert hasattr(result, 'data')  # Styled DataFrame has .data attribute
    
    # Check the underlying data
    data = result.data
    assert len(data) == 2  # Should have 2 rows (one per column)
    assert list(data.columns) == ['Column', 'Null_Count', 'Null_Percentage']


def test_check_null_columns_import_from_analysis():
    """Test check_null_columns imported directly from analysis module"""
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],  # No nulls
        'B': [1, 2, None, 4, 5],  # 20% nulls
        'C': [None, None, None, None, None],  # 100% nulls
        'D': [1, None, 3, None, 5]  # 40% nulls
    })
    
    result = check_null_columns(df, threshold=10)
    
    # Check that result is a styled DataFrame
    assert hasattr(result, 'data')  # Styled DataFrame has .data attribute
    
    # Check the underlying data
    data = result.data
    assert len(data) == 4  # Should have 4 rows (one per column)
    assert list(data.columns) == ['Column', 'Null_Count', 'Null_Percentage']
    
    # Check null percentages
    expected_percentages = [0.0, 20.0, 100.0, 40.0]
    actual_percentages = data['Null_Percentage'].tolist()
    assert actual_percentages == expected_percentages


def test_check_null_columns_custom_threshold():
    """Test check_null_columns with custom threshold"""
    df = pd.DataFrame({
        'A': [1, 2, None, 4, 5],  # 20% nulls
        'B': [1, 2, 3, 4, 5]  # 0% nulls
    })
    
    result = check_null_columns(df, threshold=25)
    data = result.data
    
    assert data['Null_Percentage'].tolist() == [20.0, 0.0]


def test_check_null_columns_no_nulls():
    """Test check_null_columns with DataFrame containing no nulls"""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c'],
        'C': [1.1, 2.2, 3.3]
    })
    
    result = check_null_columns(df)
    data = result.data
    
    assert all(data['Null_Percentage'] == 0.0)
    assert all(data['Null_Count'] == 0)


def test_analyze_categorical_columns_import():
    """Test that analyze_categorical_columns can be imported"""
    from edaflow import analyze_categorical_columns
    assert callable(analyze_categorical_columns)


def test_analyze_categorical_columns_mixed_data(capsys):
    """Test analyze_categorical_columns with mixed data types"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],  # Truly categorical
        'age_str': ['25', '30', '35'],        # Numeric stored as string
        'mixed': ['1', '2', 'three'],         # Mixed numeric/text (33% non-numeric)
        'numbers': [1, 2, 3],                 # Already numeric
        'categories': ['A', 'B', 'A']         # Categorical
    })
    
    # Import and test the function
    from edaflow import analyze_categorical_columns
    
    # Call the function (it prints to stdout)
    analyze_categorical_columns(df, threshold=35)
    
    # Capture the printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that it identifies potentially numeric columns
    assert 'age_str is potentially a numeric column' in output
    assert 'numbers is not an object column' in output
    # Mixed should be flagged as potentially numeric since 33% < 35% threshold
    assert 'mixed is potentially a numeric column' in output
    # Name and categories should be flagged as truly categorical
    assert 'name has too many non-numeric values (100.0% non-numeric)' in output
    assert 'categories has too many non-numeric values (100.0% non-numeric)' in output


def test_analyze_categorical_columns_all_numeric_strings(capsys):
    """Test analyze_categorical_columns with all numeric strings"""
    df = pd.DataFrame({
        'numeric_col': ['10', '20', '30', '40', '50']
    })
    
    from edaflow import analyze_categorical_columns
    analyze_categorical_columns(df, threshold=35)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should identify this as potentially numeric
    assert 'numeric_col is potentially a numeric column' in output
    assert "['10' '20' '30' '40' '50']" in output


def test_analyze_categorical_columns_all_text(capsys):
    """Test analyze_categorical_columns with all text data"""
    df = pd.DataFrame({
        'text_col': ['apple', 'banana', 'cherry', 'date', 'elderberry']
    })
    
    from edaflow import analyze_categorical_columns
    analyze_categorical_columns(df, threshold=35)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should identify this as truly categorical
    assert 'text_col has too many non-numeric values (100.0% non-numeric)' in output


def test_convert_to_numeric_import():
    """Test that convert_to_numeric can be imported"""
    from edaflow import convert_to_numeric
    assert callable(convert_to_numeric)


def test_convert_to_numeric_basic_conversion(capsys):
    """Test convert_to_numeric with basic string-to-numeric conversion"""
    df = pd.DataFrame({
        'numeric_str': ['10', '20', '30', '40', '50'],  # Should convert (0% non-numeric)
        'mixed': ['1', '2', 'text', '4', '5'],          # Should convert (20% < 35% threshold)
        'text_col': ['apple', 'banana', 'cherry', 'date', 'elderberry'],  # Should not convert (100% non-numeric)
        'already_numeric': [1, 2, 3, 4, 5]             # Already numeric
    })
    
    # Test with default threshold (35%)
    result_df = edaflow.convert_to_numeric(df, threshold=35)
    
    # Capture printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that the right columns were converted
    assert 'Converting numeric_str to a numerical column' in output
    assert 'Converting mixed to a numerical column' in output  # This should also convert since 20% < 35%
    assert 'text_col skipped' in output
    assert 'already_numeric skipped: already numeric' in output
    
    # Check that the DataFrame was properly modified
    assert result_df['numeric_str'].dtype in ['int64', 'float64']
    assert result_df['mixed'].dtype in ['int64', 'float64']  # Should be converted
    assert result_df['text_col'].dtype == 'object'  # Should remain object
    assert result_df['already_numeric'].dtype in ['int64', 'float64']
    
    # Check that original DataFrame is unchanged
    assert df['numeric_str'].dtype == 'object'
    assert df['mixed'].dtype == 'object'


def test_convert_to_numeric_inplace(capsys):
    """Test convert_to_numeric with inplace=True"""
    df = pd.DataFrame({
        'price': ['100', '200', '300'],
        'category': ['A', 'B', 'C']
    })
    
    original_id = id(df)
    
    # Test inplace conversion
    result = edaflow.convert_to_numeric(df, threshold=35, inplace=True)
    
    # Should return None when inplace=True
    assert result is None
    
    # Original DataFrame should be modified
    assert id(df) == original_id  # Same object
    assert df['price'].dtype in ['int64', 'float64']  # Should be converted
    assert df['category'].dtype == 'object'  # Should remain object


def test_convert_to_numeric_with_nans():
    """Test convert_to_numeric handles conversion to NaN correctly"""
    df = pd.DataFrame({
        'mixed_col': ['10', '20', 'invalid', '40'],  # 25% non-numeric
    })
    
    result_df = edaflow.convert_to_numeric(df, threshold=30)
    
    # Should convert since 25% < 30%
    assert result_df['mixed_col'].dtype in ['int64', 'float64']
    
    # Should have 1 NaN value where 'invalid' was
    assert result_df['mixed_col'].isnull().sum() == 1
    assert result_df['mixed_col'].notna().sum() == 3
    
    # Values that could be converted should be numeric
    numeric_values = result_df['mixed_col'].dropna().tolist()
    expected_values = [10.0, 20.0, 40.0]  # Will be float due to NaN presence
    assert numeric_values == expected_values


def test_convert_to_numeric_custom_threshold(capsys):
    """Test convert_to_numeric with custom threshold"""
    df = pd.DataFrame({
        'col1': ['1', '2', 'text1', 'text2'],  # 50% non-numeric
        'col2': ['10', '20', '30', '40']       # 0% non-numeric
    })
    
    # Test with strict threshold (40%)
    result_df = edaflow.convert_to_numeric(df, threshold=40)
    captured = capsys.readouterr()
    output = captured.out
    
    # col1 should be skipped (50% > 40%), col2 should be converted
    assert 'col1 skipped: 50.0% non-numeric' in output
    assert 'Converting col2 to a numerical column' in output
    
    assert result_df['col1'].dtype == 'object'
    assert result_df['col2'].dtype in ['int64', 'float64']


def test_convert_to_numeric_no_conversions(capsys):
    """Test convert_to_numeric when no conversions are possible"""
    df = pd.DataFrame({
        'text_only': ['apple', 'banana', 'cherry'],
        'already_int': [1, 2, 3],
        'already_float': [1.1, 2.2, 3.3]
    })
    
    result_df = edaflow.convert_to_numeric(df, threshold=35)
    captured = capsys.readouterr()
    output = captured.out
    
    # Should indicate no conversions were made
    assert 'No columns were converted' in output
    
    # DataFrame should be unchanged in terms of data types
    assert result_df['text_only'].dtype == 'object'
    assert result_df['already_int'].dtype in ['int64', 'float64']
    assert result_df['already_float'].dtype in ['int64', 'float64']


def test_visualize_categorical_values_import():
    """Test that visualize_categorical_values can be imported"""
    from edaflow import visualize_categorical_values
    assert callable(visualize_categorical_values)


def test_visualize_categorical_values_basic(capsys):
    """Test visualize_categorical_values with basic categorical data"""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C', 'B', 'A'],
        'status': ['active', 'inactive', 'active', 'pending', 'active', 'active'],
        'numeric_col': [1, 2, 3, 4, 5, 6]  # Should be ignored
    })
    
    # Test the function
    edaflow.visualize_categorical_values(df)
    
    # Capture printed output
    captured = capsys.readouterr()
    output = captured.out
    
    # Check that it found the right columns
    assert 'Found 2 categorical column(s): category, status' in output
    assert 'Column: category' in output
    assert 'Column: status' in output
    
    # Check that it shows values and counts
    assert "'A'" in output  # Category A
    assert "'B'" in output  # Category B
    assert "'active'" in output  # Status active
    assert 'Count:' in output  # Should show counts by default
    assert 'Most frequent:' in output  # Should show most frequent value


def test_visualize_categorical_values_no_categorical_columns(capsys):
    """Test visualize_categorical_values with no categorical columns"""
    df = pd.DataFrame({
        'numbers': [1, 2, 3, 4, 5],
        'floats': [1.1, 2.2, 3.3, 4.4, 5.5],
        'integers': [10, 20, 30, 40, 50]
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should indicate no categorical columns found
    assert 'No categorical (object-type) columns found' in output


def test_visualize_categorical_values_with_missing(capsys):
    """Test visualize_categorical_values with missing values"""
    df = pd.DataFrame({
        'category_with_nulls': ['A', 'B', None, 'A', None, 'B'],
        'complete_category': ['X', 'Y', 'X', 'Y', 'X', 'Y']
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should handle missing values
    assert 'Missing: 2' in output  # category_with_nulls has 2 NaN
    assert 'Missing: 0' in output  # complete_category has 0 NaN
    assert 'NaN/Missing' in output  # Should show NaN values


def test_visualize_categorical_values_high_cardinality(capsys):
    """Test visualize_categorical_values with high cardinality column"""
    # Create a column with many unique values
    df = pd.DataFrame({
        'high_cardinality': [f'value_{i}' for i in range(25)],  # 25 unique values
        'normal_category': ['A'] * 10 + ['B'] * 10 + ['C'] * 5
    })
    
    # Test with max_unique_values=10
    edaflow.visualize_categorical_values(df, max_unique_values=10)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should truncate high cardinality column
    assert 'Showing top 10 most frequent values (out of 25 total)' in output
    assert '... and 15 more unique value(s)' in output
    
    # Should provide insights about high cardinality
    assert 'High cardinality columns detected: high_cardinality' in output


def test_visualize_categorical_values_custom_options(capsys):
    """Test visualize_categorical_values with custom options"""
    df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'status': ['active', 'inactive', 'active', 'pending']
    })
    
    # Test with counts but no percentages
    edaflow.visualize_categorical_values(df, show_percentages=False, show_counts=True)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should show counts but not percentages
    assert 'Count:' in output
    assert '(50.0%)' not in output and '(25.0%)' not in output  # No percentages


def test_visualize_categorical_values_mostly_unique(capsys):
    """Test visualize_categorical_values with mostly unique column"""
    # Create a column where most values are unique (like IDs)
    df = pd.DataFrame({
        'mostly_unique': [f'id_{i}' for i in range(20)] + ['duplicate'] * 2,  # 20/22 are unique (>80%)
        'normal_category': ['A'] * 11 + ['B'] * 11
    })
    
    edaflow.visualize_categorical_values(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should detect mostly unique columns
    assert 'Mostly unique columns (>80% unique): mostly_unique' in output
    assert 'These might be IDs or need special handling' in output


# Tests for display_column_types function

def test_display_column_types_basic():
    """Test display_column_types with mixed data types"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'Chicago'],
        'salary': [50000, 60000, 70000],
        'is_active': [True, False, True]
    })
    
    result = display_column_types(df)
    
    # Check return type
    assert isinstance(result, dict)
    assert 'categorical' in result
    assert 'numerical' in result
    
    # Check categorical columns (object dtype)
    assert 'name' in result['categorical']
    assert 'city' in result['categorical']
    assert len(result['categorical']) == 2
    
    # Check numerical columns (non-object dtype)
    assert 'age' in result['numerical']
    assert 'salary' in result['numerical']
    assert 'is_active' in result['numerical']
    assert len(result['numerical']) == 3


def test_display_column_types_only_categorical():
    """Test display_column_types with only categorical columns"""
    df = pd.DataFrame({
        'category1': ['A', 'B', 'C'],
        'category2': ['X', 'Y', 'Z'],
        'category3': ['P', 'Q', 'R']
    })
    
    result = display_column_types(df)
    
    assert len(result['categorical']) == 3
    assert len(result['numerical']) == 0
    assert all(col in result['categorical'] for col in ['category1', 'category2', 'category3'])


def test_display_column_types_only_numerical():
    """Test display_column_types with only numerical columns"""
    df = pd.DataFrame({
        'int_col': [1, 2, 3],
        'float_col': [1.1, 2.2, 3.3],
        'bool_col': [True, False, True]
    })
    
    result = display_column_types(df)
    
    assert len(result['categorical']) == 0
    assert len(result['numerical']) == 3
    assert all(col in result['numerical'] for col in ['int_col', 'float_col', 'bool_col'])


def test_display_column_types_empty_dataframe():
    """Test display_column_types with empty DataFrame"""
    df = pd.DataFrame()
    
    result = display_column_types(df)
    
    assert result['categorical'] == []
    assert result['numerical'] == []


def test_display_column_types_invalid_input():
    """Test display_column_types with invalid input"""
    try:
        display_column_types("not a dataframe")
        assert False, "Should raise TypeError"
    except TypeError as e:
        assert "Input must be a pandas DataFrame" in str(e)


def test_display_column_types_import_from_main():
    """Test display_column_types imported from main edaflow module"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30]
    })
    
    result = edaflow.display_column_types(df)
    
    assert isinstance(result, dict)
    assert 'categorical' in result
    assert 'numerical' in result
    assert 'name' in result['categorical']
    assert 'age' in result['numerical']


def test_display_column_types_output_format(capsys):
    """Test display_column_types output format"""
    df = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30],
        'city': ['NYC', 'LA']
    })
    
    result = display_column_types(df)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Check for key output elements
    assert 'Column Type Analysis' in output
    assert 'Categorical Columns' in output
    assert 'Numerical Columns' in output
    assert 'Summary:' in output
    assert 'Total columns: 3' in output
