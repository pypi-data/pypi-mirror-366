# edaflow

A Python package for streamlined exploratory data analysis workflows.

## Description

`edaflow` is designed to simplify and accelerate the exploratory data analysis (EDA) process by providing a collection of tools and utilities for data scientists and analysts. The package integrates popular data science libraries to create a cohesive workflow for data exploration, visualization, and preprocessing.

## Features

- **Missing Data Analysis**: Color-coded analysis of null values with customizable thresholds
- **Categorical Data Insights**: Identify object columns that might be numeric, detect data type issues
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

# Step 3: Based on the analysis, you can then:
# - Convert string numbers to numeric types
# - Handle missing data appropriately
# - Clean categorical data

# Example conversion based on analysis results:
# df['price'] = pd.to_numeric(df['price_str'], errors='coerce')
# df = df.drop('price_str', axis=1)
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