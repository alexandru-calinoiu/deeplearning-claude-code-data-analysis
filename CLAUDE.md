# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

E-commerce business analytics solution with modular Python architecture. The project transforms raw CSV datasets into actionable business insights through both Jupyter notebook analysis and a professional Streamlit dashboard.

## Data Architecture

The system processes 6 CSV datasets from `ecommerce_data/`:
- `orders_dataset.csv` - Order records with timestamps and status
- `order_items_dataset.csv` - Line items with pricing
- `products_dataset.csv` - Product catalog with categories
- `customers_dataset.csv` - Customer geographic data
- `order_reviews_dataset.csv` - Review scores (1-5 scale)
- `order_payments_dataset.csv` - Payment information

**Data Flow**: Raw CSVs → `EcommerceDataLoader` → Processed DataFrames → `BusinessMetricsCalculator` → Visualizations

## Core Module Architecture

### data_loader.py
Central data processing module with `EcommerceDataLoader` class:

- **load_raw_data()**: Reads all CSV files into dictionary of DataFrames
- **clean_orders_data()**: Parses timestamps, extracts year/month components
- **clean_order_items_data()**: Calculates total_item_value (price + freight)
- **create_sales_dataset()**: Joins all tables with configurable filters (year, month, status)
  - Default status filter: `'delivered'` (only completed orders)
  - Joins: order_items → orders → products → customers → reviews
  - Calculates `delivery_days` metric automatically

### business_metrics.py
Business intelligence calculation module with two main classes:

**BusinessMetricsCalculator**:
- `calculate_revenue_metrics()`: Total revenue, AOV, growth rates (YoY comparison)
- `calculate_monthly_trends()`: MoM growth, revenue patterns
- `analyze_product_performance()`: Category revenue share, top performers
- `analyze_geographic_performance()`: State-level revenue aggregation
- `analyze_customer_satisfaction()`: Review score statistics
- `analyze_delivery_performance()`: Delivery time categorization
- `generate_comprehensive_report()`: All metrics combined

**MetricsVisualizer**:
- Uses matplotlib for static plots and plotly for interactive charts
- Professional formatting with currency symbols and percentages

### dashboard.py
Streamlit web application with responsive grid layout:

- **KPI Cards**: 4-column metric display with YoY trend indicators
- **Charts Grid**: 2×2 layout (revenue trend, categories, geographic map, satisfaction)
- **Customer Experience**: Delivery time and review score cards
- **@st.cache_data**: Caches data loading for performance
- Custom CSS for professional styling with metric cards

## Common Development Commands

### Running the Dashboard
```bash
streamlit run dashboard.py
```
Dashboard runs on http://localhost:8501 with hot-reload enabled.

### Running Jupyter Analysis
```bash
jupyter notebook EDA_Refactored.ipynb
```
or
```bash
jupyter lab
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Key Configuration Parameters

In notebooks, configure analysis at the top:
```python
ANALYSIS_YEAR = 2023        # Primary year to analyze
COMPARISON_YEAR = 2022      # For YoY calculations
ANALYSIS_MONTH = None       # None for full year, or 1-12 for specific month
DATA_PATH = 'ecommerce_data/'
```

The dashboard uses year/month selectors in the UI, defaulting to 2023.

## Data Filtering Pattern

All analysis uses the same filtering approach via `create_sales_dataset()`:
- **year_filter**: Required for most analyses (int)
- **month_filter**: Optional, None for full year (int or None)
- **status_filter**: Default 'delivered' to exclude cancelled/pending orders (str)

To analyze different time periods, call `create_sales_dataset()` with different parameters rather than manually filtering DataFrames.

## Metric Calculation Notes

- **Revenue**: Sum of `price` column (excludes freight in revenue totals)
- **AOV (Average Order Value)**: Total revenue / unique order count
- **Delivery Days**: Calculated as `order_delivered_customer_date - order_purchase_timestamp`
- **Delivery Speed Categories**: 1-3 days (fast), 4-7 days (medium), 8+ days (slow)
- **High Satisfaction**: Review score ≥ 4

Growth rates use YoY comparison: `((current - previous) / previous) * 100`

## Geographic Data Specifics

The geographic analysis uses US state abbreviations in `customer_state` column. The choropleth map visualization requires:
- `locationmode='USA-states'`
- `scope='usa'`
- State codes must match standard US postal abbreviations

## Important Conventions

1. **Order-level vs Item-level**: Many analyses require deduplication by `order_id` (reviews, delivery metrics) while revenue uses item-level data
2. **Date Handling**: All timestamp columns are converted to pandas datetime in `clean_orders_data()`
3. **Missing Data**: Modules handle missing columns gracefully with error messages rather than exceptions
4. **Currency Formatting**: Dashboard uses K/M suffixes (`format_currency()` function)

## Testing Data Availability

Before running analyses, verify data is loaded:
```python
loader, processed_data = load_and_process_data('ecommerce_data/')
summary = loader.get_data_summary()
```

Check date ranges to ensure year filters match available data.
