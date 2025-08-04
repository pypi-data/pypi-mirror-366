"""
Tests for the main edaflow module
"""
import pandas as pd
import edaflow
from edaflow.analysis import check_null_columns, analyze_categorical_columns


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
