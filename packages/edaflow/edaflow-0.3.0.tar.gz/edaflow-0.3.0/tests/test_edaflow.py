"""
Tests for the main edaflow module
"""
import pandas as pd
import edaflow
from edaflow.analysis import check_null_columns, analyze_categorical_columns, convert_to_numeric


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
