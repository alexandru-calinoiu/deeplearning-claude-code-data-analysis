# E-Commerce Business Analytics

A comprehensive e-commerce analytics solution with modular Python architecture for analyzing sales performance, product trends, geographic distribution, and customer satisfaction.

## Project Structure

```
.
├── data_loader.py              # Data loading and cleaning module
├── business_metrics.py         # Business metrics calculation and visualization
├── EDA_Refactored.ipynb        # Main analysis notebook
├── EDA.ipynb                   # Original exploratory analysis
├── requirements.txt            # Python dependencies
├── ecommerce_data/            # Data directory (CSV files)
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   ├── customers_dataset.csv
│   └── order_reviews_dataset.csv
└── README.md                   # This file
```

## Features

- **Revenue Analysis**: Total revenue, year-over-year growth, monthly trends
- **Product Performance**: Category-level analysis with revenue share
- **Geographic Analysis**: State-level revenue distribution with interactive maps
- **Customer Experience**: Review scores and delivery performance correlation
- **Configurable Analysis**: Flexible date filtering by year and month

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Refactored Analysis

1. **Start Jupyter Notebook:**
```bash
jupyter notebook
```

2. **Open the notebook:**
   - Navigate to `EDA_Refactored.ipynb` in the Jupyter interface

3. **Configure analysis parameters:**
   - In the "Data Loading and Configuration" section, modify:
     - `ANALYSIS_YEAR`: Primary year to analyze (default: 2023)
     - `COMPARISON_YEAR`: Year for comparison (default: 2022)
     - `ANALYSIS_MONTH`: Specific month (1-12) or None for full year
     - `DATA_PATH`: Path to data directory

4. **Run all cells:**
   - Click "Cell" → "Run All" or use Shift+Enter to run cells sequentially

### Analysis Examples

**Analyze full year 2023:**
```python
ANALYSIS_YEAR = 2023
COMPARISON_YEAR = 2022
ANALYSIS_MONTH = None  # Full year
```

**Analyze specific month (e.g., December 2023):**
```python
ANALYSIS_YEAR = 2023
COMPARISON_YEAR = 2022
ANALYSIS_MONTH = 12
```

**Compare Q4 2023 vs Q4 2022:**
Run the analysis three times for months 10, 11, and 12, then aggregate results.

## Module Documentation

### data_loader.py

Handles all data loading and cleaning operations.

**Key Class: `EcommerceDataLoader`**

Methods:
- `load_raw_data()`: Load all CSV files
- `clean_orders_data()`: Parse timestamps, extract year/month
- `clean_order_items_data()`: Calculate total item values
- `create_sales_dataset(year_filter, month_filter, status_filter)`: Create filtered analysis dataset
- `get_data_summary()`: Get overview statistics

**Convenience Function:**
```python
from data_loader import load_and_process_data

loader, processed_data = load_and_process_data('ecommerce_data/')
```

### business_metrics.py

Calculates business metrics and creates visualizations.

**Key Class: `BusinessMetricsCalculator`**

Methods:
- `calculate_revenue_metrics(comparison_data)`: Revenue, AOV, growth rates
- `calculate_monthly_trends()`: Month-over-month analysis
- `analyze_product_performance()`: Category-level metrics
- `analyze_geographic_performance()`: State-level analysis
- `analyze_customer_satisfaction()`: Review score statistics
- `analyze_delivery_performance()`: Delivery time analysis
- `generate_comprehensive_report(comparison_data)`: All metrics combined

**Key Class: `MetricsVisualizer`**

Static methods for creating visualizations:
- `plot_revenue_trend()`: Monthly revenue line chart
- `plot_category_performance()`: Product category bar chart
- `plot_geographic_map()`: Interactive state choropleth map
- `plot_review_distribution()`: Review score distribution
- `plot_delivery_performance()`: Delivery speed vs satisfaction

### Example Usage in Code

```python
from data_loader import load_and_process_data
from business_metrics import BusinessMetricsCalculator, MetricsVisualizer

# Load data
loader, processed_data = load_and_process_data('ecommerce_data/')

# Create filtered dataset
sales_2023 = loader.create_sales_dataset(
    year_filter=2023,
    month_filter=None,
    status_filter='delivered'
)

# Calculate metrics
calculator = BusinessMetricsCalculator(sales_2023)
revenue_metrics = calculator.calculate_revenue_metrics()

# Create visualization
visualizer = MetricsVisualizer()
monthly_trends = calculator.calculate_monthly_trends()
fig = visualizer.plot_revenue_trend(monthly_trends)
```

## Data Dictionary

### Input Data

**orders_dataset.csv**
- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `order_status`: delivered, shipped, canceled, pending, processing, returned
- `order_purchase_timestamp`: Order placement datetime
- `order_delivered_customer_date`: Delivery datetime

**order_items_dataset.csv**
- `order_id`: Links to orders table
- `product_id`: Links to products table
- `price`: Product price (USD)
- `freight_value`: Shipping cost (USD)

**products_dataset.csv**
- `product_id`: Unique product identifier
- `product_category_name`: Product category

**customers_dataset.csv**
- `customer_id`: Unique customer identifier
- `customer_state`: US state abbreviation
- `customer_city`: City name

**order_reviews_dataset.csv**
- `order_id`: Links to orders table
- `review_score`: Customer rating (1-5, 5 is best)

### Calculated Metrics

- **Revenue**: Sum of order item prices (excludes freight)
- **Average Order Value (AOV)**: Total revenue / number of orders
- **Delivery Days**: Days between purchase and delivery
- **Delivery Speed Categories**:
  - Fast: 1-3 days
  - Medium: 4-7 days
  - Slow: 8+ days
- **High Satisfaction**: Review score >= 4

## Output and Visualizations

The notebook generates:

1. **Revenue Metrics**
   - Total revenue with YoY comparison
   - Monthly trend line chart
   - Average order value

2. **Product Analysis**
   - Top 10 categories bar chart
   - Revenue share percentages
   - Category performance table

3. **Geographic Analysis**
   - Interactive US state choropleth map
   - Top states ranking
   - State-level revenue distribution

4. **Customer Experience**
   - Review score distribution chart
   - Average satisfaction score
   - Delivery performance analysis
   - Correlation between delivery speed and satisfaction

## Customization

### Adding New Metrics

1. **Add calculation method to `BusinessMetricsCalculator`:**
```python
def calculate_custom_metric(self) -> Dict[str, float]:
    # Your calculation logic
    return metrics
```

2. **Add visualization to `MetricsVisualizer`:**
```python
@staticmethod
def plot_custom_metric(data, title):
    # Your plotting logic
    return fig
```

3. **Use in notebook:**
```python
custom_metrics = calculator.calculate_custom_metric()
fig = visualizer.plot_custom_metric(data, title)
```

### Filtering by Order Status

The default analysis includes only 'delivered' orders. To include other statuses:

```python
sales_all_statuses = loader.create_sales_dataset(
    year_filter=2023,
    status_filter=None  # Include all statuses
)
```

Available statuses: delivered, shipped, canceled, pending, processing, returned

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'data_loader'`
- **Solution**: Ensure you're running the notebook from the project root directory

**Issue**: `FileNotFoundError: ecommerce_data/orders_dataset.csv`
- **Solution**: Verify the `DATA_PATH` configuration points to the correct directory

**Issue**: Empty dataset after filtering
- **Solution**: Check that `ANALYSIS_YEAR` exists in the data using `loader.get_data_summary()`

**Issue**: Plots not displaying
- **Solution**: Ensure `%matplotlib inline` is executed and matplotlib is installed

## Performance Notes

- Loading all data typically takes 2-5 seconds
- Full year analysis with all visualizations runs in ~10-15 seconds
- Monthly trends visualization is only available for full year analysis

## Contributing

To extend this analysis:

1. Add new metric calculations to `business_metrics.py`
2. Create new visualization methods in `MetricsVisualizer`
3. Update notebook cells to use new metrics
4. Document new features in this README

## License

This project is for educational and business analysis purposes.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.
