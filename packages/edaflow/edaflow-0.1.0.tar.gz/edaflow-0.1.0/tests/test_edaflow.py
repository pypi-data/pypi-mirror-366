"""
Tests for the main edaflow module
"""
import pandas as pd
import edaflow
from edaflow.analysis import check_null_columns


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
