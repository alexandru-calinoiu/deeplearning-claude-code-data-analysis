"""
Data loading and cleaning module for e-commerce analytics.

This module provides the EcommerceDataLoader class for loading, cleaning, and
preparing e-commerce datasets for analysis.
"""

import pandas as pd
import os
from typing import Dict, Optional


class EcommerceDataLoader:
    """
    Handles loading and cleaning of e-commerce datasets.

    Attributes:
        data_path (str): Path to the directory containing CSV files
        raw_data (dict): Dictionary storing raw DataFrames
        processed_data (dict): Dictionary storing processed DataFrames
    """

    def __init__(self, data_path: str = 'ecommerce_data/'):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the directory containing CSV files
        """
        self.data_path = data_path
        self.raw_data = {}
        self.processed_data = {}

    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files from the data directory.

        Returns:
            Dictionary of DataFrames with dataset names as keys
        """
        datasets = {
            'orders': 'orders_dataset.csv',
            'order_items': 'order_items_dataset.csv',
            'products': 'products_dataset.csv',
            'customers': 'customers_dataset.csv',
            'reviews': 'order_reviews_dataset.csv'
        }

        for name, filename in datasets.items():
            filepath = os.path.join(self.data_path, filename)
            self.raw_data[name] = pd.read_csv(filepath)

        return self.raw_data

    def clean_orders_data(self) -> pd.DataFrame:
        """
        Clean and process orders data.

        Converts timestamp columns to datetime and extracts year/month components.

        Returns:
            Cleaned orders DataFrame
        """
        orders = self.raw_data['orders'].copy()

        # Convert timestamp columns to datetime
        timestamp_cols = [
            'order_purchase_timestamp',
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]

        for col in timestamp_cols:
            if col in orders.columns:
                orders[col] = pd.to_datetime(orders[col])

        # Extract year and month from purchase timestamp
        orders['year'] = orders['order_purchase_timestamp'].dt.year
        orders['month'] = orders['order_purchase_timestamp'].dt.month

        self.processed_data['orders'] = orders
        return orders

    def clean_order_items_data(self) -> pd.DataFrame:
        """
        Clean and process order items data.

        Calculates total item value (price + freight).

        Returns:
            Cleaned order items DataFrame
        """
        order_items = self.raw_data['order_items'].copy()

        # Calculate total item value
        order_items['total_item_value'] = order_items['price'] + order_items['freight_value']

        self.processed_data['order_items'] = order_items
        return order_items

    def clean_customers_data(self) -> pd.DataFrame:
        """
        Clean and process customers data.

        Returns:
            Cleaned customers DataFrame
        """
        customers = self.raw_data['customers'].copy()
        self.processed_data['customers'] = customers
        return customers

    def clean_products_data(self) -> pd.DataFrame:
        """
        Clean and process products data.

        Returns:
            Cleaned products DataFrame
        """
        products = self.raw_data['products'].copy()
        self.processed_data['products'] = products
        return products

    def clean_reviews_data(self) -> pd.DataFrame:
        """
        Clean and process reviews data.

        Returns:
            Cleaned reviews DataFrame
        """
        reviews = self.raw_data['reviews'].copy()

        # Convert timestamp columns to datetime
        if 'review_creation_date' in reviews.columns:
            reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
        if 'review_answer_timestamp' in reviews.columns:
            reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'])

        self.processed_data['reviews'] = reviews
        return reviews

    def create_sales_dataset(
        self,
        year_filter: Optional[int] = None,
        month_filter: Optional[int] = None,
        status_filter: str = 'delivered'
    ) -> pd.DataFrame:
        """
        Create a comprehensive sales dataset by merging all relevant tables.

        Args:
            year_filter: Filter data by specific year (e.g., 2023)
            month_filter: Filter data by specific month (1-12)
            status_filter: Filter by order status (default: 'delivered')

        Returns:
            Merged DataFrame containing sales data with all relevant dimensions
        """
        # Start with order items
        sales = self.processed_data['order_items'][
            ['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']
        ].copy()

        # Merge with orders
        orders_cols = [
            'order_id', 'customer_id', 'order_status',
            'order_purchase_timestamp', 'order_delivered_customer_date',
            'year', 'month'
        ]
        sales = pd.merge(
            sales,
            self.processed_data['orders'][orders_cols],
            on='order_id',
            how='left'
        )

        # Apply filters
        if status_filter:
            sales = sales[sales['order_status'] == status_filter].copy()

        if year_filter:
            sales = sales[sales['year'] == year_filter].copy()

        if month_filter:
            sales = sales[sales['month'] == month_filter].copy()

        # Merge with products
        products_cols = ['product_id', 'product_category_name']
        sales = pd.merge(
            sales,
            self.processed_data['products'][products_cols],
            on='product_id',
            how='left'
        )

        # Merge with customers
        customers_cols = ['customer_id', 'customer_state', 'customer_city']
        sales = pd.merge(
            sales,
            self.processed_data['customers'][customers_cols],
            on='customer_id',
            how='left'
        )

        # Merge with reviews
        reviews_cols = ['order_id', 'review_score']
        sales = pd.merge(
            sales,
            self.processed_data['reviews'][reviews_cols],
            on='order_id',
            how='left'
        )

        # Calculate delivery days
        sales['delivery_days'] = (
            sales['order_delivered_customer_date'] - sales['order_purchase_timestamp']
        ).dt.days

        return sales

    def get_data_summary(self) -> Dict[str, any]:
        """
        Get summary statistics about the loaded datasets.

        Returns:
            Dictionary containing summary information
        """
        if not self.processed_data:
            return {"error": "No data loaded yet"}

        summary = {}

        if 'orders' in self.processed_data:
            orders = self.processed_data['orders']
            summary['total_orders'] = len(orders)
            summary['date_range'] = {
                'start': orders['order_purchase_timestamp'].min(),
                'end': orders['order_purchase_timestamp'].max()
            }
            summary['years_available'] = sorted(orders['year'].unique().tolist())
            summary['order_statuses'] = orders['order_status'].value_counts().to_dict()

        if 'products' in self.processed_data:
            summary['total_products'] = len(self.processed_data['products'])
            summary['product_categories'] = self.processed_data['products']['product_category_name'].nunique()

        if 'customers' in self.processed_data:
            summary['total_customers'] = len(self.processed_data['customers'])
            summary['states'] = self.processed_data['customers']['customer_state'].nunique()

        return summary


def load_and_process_data(data_path: str = 'ecommerce_data/') -> tuple:
    """
    Convenience function to load and process all data at once.

    Args:
        data_path: Path to the directory containing CSV files

    Returns:
        Tuple of (EcommerceDataLoader instance, processed_data dictionary)
    """
    loader = EcommerceDataLoader(data_path)
    loader.load_raw_data()
    loader.clean_orders_data()
    loader.clean_order_items_data()
    loader.clean_products_data()
    loader.clean_customers_data()
    loader.clean_reviews_data()

    return loader, loader.processed_data
