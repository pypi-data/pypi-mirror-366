# edaflow

A Python package for streamlined exploratory data analysis workflows.

## Description

`edaflow` is designed to simplify and accelerate the exploratory data analysis (EDA) process by providing a collection of tools and utilities for data scientists and analysts. The package integrates popular data science libraries to create a cohesive workflow for data exploration, visualization, and preprocessing.

## Features

- **Missing Data Analysis**: Color-coded analysis of null values with customizable thresholds
- **Categorical Data Insights**: Identify object columns that might be numeric, detect data type issues
- **Automatic Data Type Conversion**: Smart conversion of object columns to numeric when appropriate
- **Categorical Values Visualization**: Detailed exploration of categorical column values with insights
- **Column Type Classification**: Simple categorization of DataFrame columns into categorical and numerical types
- **Data Type Detection**: Smart analysis to flag potential data conversion needs
- **Styled Output**: Beautiful, color-coded results for Jupyter notebooks and terminals
- **Easy Integration**: Works seamlessly with pandas, numpy, and other popular libraries

## Installation

### From PyPI
```bash
pip install edaflow
```

### From Source
```bash
git clone https://github.com/evanlow/edaflow.git
cd edaflow
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/evanlow/edaflow.git
cd edaflow
pip install -e ".[dev]"
```

## Requirements

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0
- scipy >= 1.7.0
- missingno >= 0.5.0

## Quick Start

```python
import edaflow

# Test the installation
print(edaflow.hello())

# Check null values in your dataset
import pandas as pd
df = pd.read_csv('your_data.csv')

# Analyze missing data with styled output
null_analysis = edaflow.check_null_columns(df, threshold=10)
print(null_analysis)

# Analyze categorical columns to identify data type issues
edaflow.analyze_categorical_columns(df, threshold=35)

# Convert appropriate object columns to numeric automatically
df_cleaned = edaflow.convert_to_numeric(df, threshold=35)
print("Data types after conversion:", df_cleaned.dtypes)
```

## Usage Examples

### Basic Usage
```python
import edaflow

# Verify installation
message = edaflow.hello()
print(message)  # Output: "Hello from edaflow! Ready for exploratory data analysis."
```

### Missing Data Analysis with `check_null_columns`

The `check_null_columns` function provides a color-coded analysis of missing data in your DataFrame:

```python
import pandas as pd
import edaflow

# Create sample data with missing values
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', None, 'Diana', 'Eve'],
    'age': [25, None, 35, None, 45],
    'email': [None, None, None, None, None],  # All missing
    'purchase_amount': [100.5, 250.0, 75.25, None, 320.0]
})

# Analyze missing data with default threshold (10%)
styled_result = edaflow.check_null_columns(df)
styled_result  # Display in Jupyter notebook for color-coded styling

# Use custom threshold (20%) to change color coding sensitivity
styled_result = edaflow.check_null_columns(df, threshold=20)
styled_result

# Access underlying data if needed
data = styled_result.data
print(data)
```

**Color Coding:**
- 🔴 **Red**: > 20% missing (high concern)
- 🟡 **Yellow**: 10-20% missing (medium concern)  
- 🟨 **Light Yellow**: 1-10% missing (low concern)
- ⬜ **Gray**: 0% missing (no issues)

### Categorical Data Analysis with `analyze_categorical_columns`

The `analyze_categorical_columns` function helps identify data type issues and provides insights into object-type columns:

```python
import pandas as pd
import edaflow

# Create sample data with mixed categorical types
df = pd.DataFrame({
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'price_str': ['999', '25', '75', '450'],  # Numbers stored as strings
    'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics'],
    'rating': [4.5, 3.8, 4.2, 4.7],  # Already numeric
    'mixed_ids': ['001', '002', 'ABC', '004'],  # Mixed format
    'status': ['active', 'inactive', 'active', 'pending']
})

# Analyze categorical columns with default threshold (35%)
edaflow.analyze_categorical_columns(df)

# Use custom threshold (50%) to be more lenient about mixed data
edaflow.analyze_categorical_columns(df, threshold=50)
```

**Output Interpretation:**
- 🔴🔵 **Highlighted in Red/Blue**: Potentially numeric columns that might need conversion
- 🟡⚫ **Highlighted in Yellow/Black**: Shows unique values for potential numeric columns
- **Regular text**: Truly categorical columns with statistics
- **"not an object column"**: Already properly typed numeric columns

### Data Type Conversion with `convert_to_numeric`

After analyzing your categorical columns, you can automatically convert appropriate columns to numeric:

```python
import pandas as pd
import edaflow

# Create sample data with string numbers
df = pd.DataFrame({
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'price_str': ['999', '25', '75', '450'],      # Should convert
    'mixed_ids': ['001', '002', 'ABC', '004'],    # Mixed data
    'category': ['Electronics', 'Accessories', 'Electronics', 'Electronics']
})

# Convert appropriate columns to numeric (threshold=35% by default)
df_converted = edaflow.convert_to_numeric(df, threshold=35)

# Or modify the original DataFrame in place
edaflow.convert_to_numeric(df, threshold=35, inplace=True)

# Use a stricter threshold (only convert if <20% non-numeric values)
df_strict = edaflow.convert_to_numeric(df, threshold=20)
```

**Function Features:**
- ✅ **Smart Detection**: Only converts columns with few non-numeric values
- ✅ **Customizable Threshold**: Control conversion sensitivity 
- ✅ **Safe Conversion**: Non-numeric values become NaN (not errors)
- ✅ **Inplace Option**: Modify original DataFrame or create new one
- ✅ **Detailed Output**: Shows exactly what was converted and why

### Categorical Data Visualization with `visualize_categorical_values`

After cleaning your data, explore categorical columns in detail to understand value distributions:

```python
import pandas as pd
import edaflow

# Example DataFrame with categorical data
df = pd.DataFrame({
    'department': ['Sales', 'Marketing', 'Sales', 'HR', 'Marketing', 'Sales', 'IT'],
    'status': ['Active', 'Inactive', 'Active', 'Pending', 'Active', 'Active', 'Inactive'],
    'priority': ['High', 'Medium', 'High', 'Low', 'Medium', 'High', 'Low'],
    'employee_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007],  # Numeric (ignored)
    'salary': [50000, 60000, 55000, 45000, 58000, 62000, 70000]  # Numeric (ignored)
})

# Visualize all categorical columns
edaflow.visualize_categorical_values(df)
```

**Advanced Usage Examples:**

```python
# Handle high-cardinality data (many unique values)
large_df = pd.DataFrame({
    'product_id': [f'PROD_{i:04d}' for i in range(100)],  # 100 unique values
    'category': ['Electronics'] * 40 + ['Clothing'] * 35 + ['Books'] * 25,
    'status': ['Available'] * 80 + ['Out of Stock'] * 15 + ['Discontinued'] * 5
})

# Limit display for high-cardinality columns
edaflow.visualize_categorical_values(large_df, max_unique_values=5)
```

```python
# DataFrame with missing values for comprehensive analysis
df_with_nulls = pd.DataFrame({
    'region': ['North', 'South', None, 'East', 'West', 'North', None],
    'customer_type': ['Premium', 'Standard', 'Premium', None, 'Standard', 'Premium', 'Standard'],
    'transaction_id': [f'TXN_{i}' for i in range(7)],  # Mostly unique (ID-like)
})

# Get detailed insights including missing value analysis
edaflow.visualize_categorical_values(df_with_nulls)
```

**Function Features:**
- 🎯 **Smart Column Detection**: Automatically finds categorical (object-type) columns
- 📊 **Value Distribution**: Shows counts and percentages for each unique value  
- 🔍 **Missing Value Analysis**: Tracks and reports NaN/missing values
- ⚡ **High-Cardinality Handling**: Truncates display for columns with many unique values
- 💡 **Actionable Insights**: Identifies ID-like columns and provides data quality recommendations
- 🎨 **Color-Coded Output**: Easy-to-read formatted results with highlighting

### Column Type Classification with `display_column_types`

The `display_column_types` function provides a simple way to categorize DataFrame columns into categorical and numerical types:

```python
import pandas as pd
import edaflow

# Create sample data with mixed types
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago'],
    'salary': [50000, 60000, 70000],
    'is_active': [True, False, True]
}
df = pd.DataFrame(data)

# Display column type classification
result = edaflow.display_column_types(df)

# Access the categorized column lists
categorical_cols = result['categorical']  # ['name', 'city']
numerical_cols = result['numerical']      # ['age', 'salary', 'is_active']
```

**Example Output:**
```
📊 Column Type Analysis
==================================================

📝 Categorical Columns (2 total):
    1. name                 (unique values: 3)
    2. city                 (unique values: 3)

🔢 Numerical Columns (3 total):
    1. age                  (dtype: int64)
    2. salary               (dtype: int64)
    3. is_active            (dtype: bool)

📈 Summary:
   Total columns: 5
   Categorical: 2 (40.0%)
   Numerical: 3 (60.0%)
```

**Function Features:**
- 🔍 **Simple Classification**: Separates columns into categorical (object dtype) and numerical (all other dtypes)
- 📊 **Detailed Information**: Shows unique value counts for categorical columns and data types for numerical columns
- 📈 **Summary Statistics**: Provides percentage breakdown of column types
- 🎯 **Return Values**: Returns dictionary with categorized column lists for programmatic use
- ⚡ **Fast Processing**: Efficient classification based on pandas data types
- 🛡️ **Error Handling**: Validates input and handles edge cases like empty DataFrames

### Complete EDA Workflow Example

```python
import pandas as pd
import edaflow

# Load your dataset
df = pd.read_csv('customer_data.csv')

print("=== EXPLORATORY DATA ANALYSIS WITH EDAFLOW ===")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Step 1: Check for missing data
print("\n1. MISSING DATA ANALYSIS")
print("-" * 40)
null_analysis = edaflow.check_null_columns(df, threshold=15)
null_analysis  # Shows color-coded missing data summary

# Step 2: Analyze categorical columns for data type issues
print("\n2. CATEGORICAL DATA ANALYSIS")  
print("-" * 40)
edaflow.analyze_categorical_columns(df, threshold=30)

# Step 3: Convert appropriate columns to numeric automatically
print("\n3. AUTOMATIC DATA TYPE CONVERSION")
print("-" * 40)
df_cleaned = edaflow.convert_to_numeric(df, threshold=30)

# Step 4: Visualize categorical column values in detail
print("\n4. CATEGORICAL VALUES EXPLORATION")
print("-" * 40)
edaflow.visualize_categorical_values(df_cleaned, max_unique_values=10)

# Step 5: Display column type classification
print("\n5. COLUMN TYPE CLASSIFICATION")
print("-" * 40)
column_types = edaflow.display_column_types(df_cleaned)

# Step 6: Final data review
print("\n6. DATA CLEANING SUMMARY")
print("-" * 40)
print("Original data types:")
print(df.dtypes)
print("\nCleaned data types:")
print(df_cleaned.dtypes)
print(f"\nFinal dataset shape: {df_cleaned.shape}")

# Now your data is ready for further analysis!
# You can proceed with:
# - Statistical analysis
# - Machine learning preprocessing
# - Visualization
# - Advanced EDA techniques
```

### Integration with Jupyter Notebooks

For the best experience, use these functions in Jupyter notebooks where:
- `check_null_columns()` displays beautiful color-coded tables
- `analyze_categorical_columns()` shows colored terminal output
- You can iterate quickly on data cleaning decisions

```python
# In Jupyter notebook cell
import pandas as pd
import edaflow

df = pd.read_csv('your_data.csv')

# This will display a nicely formatted, color-coded table
edaflow.check_null_columns(df)
```

# Load your dataset
df = pd.read_csv('data.csv')

# Analyze categorical columns to identify potential issues
edaflow.analyze_categorical_columns(df, threshold=35)

# This will identify:
# - Object columns that might actually be numeric (need conversion)
# - Truly categorical columns with their unique values
# - Mixed data type issues
```

### Working with Data (Future Implementation)
```python
import pandas as pd
import edaflow

# Load your dataset
df = pd.read_csv('data.csv')

# Perform EDA workflow
# summary = edaflow.quick_summary(df)
# edaflow.plot_overview(df)
# clean_df = edaflow.clean_data(df)
```

## Project Structure

```
edaflow/
├── edaflow/
│   ├── __init__.py
│   ├── analysis/
│   ├── visualization/
│   └── preprocessing/
├── tests/
├── docs/
├── examples/
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/evanlow/edaflow.git
cd edaflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 edaflow/
black edaflow/
isort edaflow/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.3.1 (Feature Enhancement)
- **NEW**: `display_column_types()` function for column type classification
- **NEW**: Complete 5-function EDA workflow: analyze → convert → visualize → classify
- **ENHANCED**: Updated comprehensive examples with full 5-function workflow
- Enhanced testing coverage with 32 comprehensive tests covering all functions

### v0.3.0 (Major Feature Release)
- **NEW**: `convert_to_numeric()` function for automatic data type conversion
- **NEW**: `visualize_categorical_values()` function for detailed categorical data exploration
- **NEW**: Smart threshold-based conversion with detailed reporting
- **NEW**: Inplace conversion option for flexible DataFrame modification
- **NEW**: Safe conversion with NaN handling for invalid values
- **NEW**: High-cardinality handling and data quality insights
- Enhanced testing coverage with comprehensive tests

### v0.2.1 (Documentation Enhancement)
- **ENHANCED**: Comprehensive README with detailed usage examples
- **NEW**: Step-by-step examples for both `check_null_columns()` and `analyze_categorical_columns()`
- **NEW**: Complete EDA workflow example showing real-world usage
- **NEW**: Jupyter notebook integration examples
- **IMPROVED**: Color-coding explanations and output interpretation guides

### v0.2.0 (Feature Release)
- **NEW**: `analyze_categorical_columns()` function for categorical data analysis
- **NEW**: Smart detection of object columns that might be numeric
- **NEW**: Color-coded terminal output for better readability
- Enhanced testing coverage with 12 comprehensive tests
- Improved documentation with detailed usage examples

### v0.1.1 (Documentation Update)
- Updated README with improved acknowledgments
- Fixed GitHub repository URLs
- Enhanced PyPI package presentation

### v0.1.0 (Initial Release)
- Basic package structure
- Sample hello() function
- `check_null_columns()` function for missing data analysis
- Core dependencies setup
- Documentation framework

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub repository](https://github.com/evanlow/edaflow/issues).

## Roadmap

- [ ] Core analysis modules
- [ ] Visualization utilities
- [ ] Data preprocessing tools
- [ ] Missing data handling
- [ ] Statistical testing suite
- [ ] Interactive dashboards
- [ ] CLI interface
- [ ] Documentation website

## Acknowledgments

edaflow was developed during the AI/ML course conducted by NTUC LearningHub. I am grateful for the privilege of working alongside my coursemates from Cohort 15. A special thanks to our awesome instructor, Ms. Isha Sehgal, who not only inspired us but also instilled the data science discipline that we now possess