"""
Business metrics calculation and visualization module for e-commerce analytics.

This module provides classes for calculating key business metrics and creating
visualizations for e-commerce data analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from typing import Dict, Optional, Tuple


class BusinessMetricsCalculator:
    """
    Calculates various business metrics from e-commerce data.

    Attributes:
        sales_data (pd.DataFrame): The sales dataset to analyze
    """

    def __init__(self, sales_data: pd.DataFrame):
        """
        Initialize the metrics calculator.

        Args:
            sales_data: DataFrame containing sales data with all dimensions
        """
        self.sales_data = sales_data

    def calculate_revenue_metrics(
        self,
        comparison_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """
        Calculate revenue-related metrics.

        Args:
            comparison_data: Optional DataFrame for comparison (e.g., previous year)

        Returns:
            Dictionary containing revenue metrics
        """
        metrics = {}

        # Total revenue
        metrics['total_revenue'] = self.sales_data['price'].sum()

        # Average order value (AOV)
        order_totals = self.sales_data.groupby('order_id')['price'].sum()
        metrics['average_order_value'] = order_totals.mean()
        metrics['median_order_value'] = order_totals.median()

        # Total orders
        metrics['total_orders'] = self.sales_data['order_id'].nunique()

        # Total items sold
        metrics['total_items'] = len(self.sales_data)

        # Items per order
        metrics['avg_items_per_order'] = metrics['total_items'] / metrics['total_orders']

        # Comparison metrics (YoY growth)
        if comparison_data is not None:
            prev_revenue = comparison_data['price'].sum()
            prev_orders = comparison_data['order_id'].nunique()
            prev_aov = comparison_data.groupby('order_id')['price'].sum().mean()

            if prev_revenue > 0:
                metrics['revenue_growth_pct'] = (
                    (metrics['total_revenue'] - prev_revenue) / prev_revenue * 100
                )
            else:
                metrics['revenue_growth_pct'] = None

            if prev_orders > 0:
                metrics['order_growth_pct'] = (
                    (metrics['total_orders'] - prev_orders) / prev_orders * 100
                )
            else:
                metrics['order_growth_pct'] = None

            if prev_aov > 0:
                metrics['aov_growth_pct'] = (
                    (metrics['average_order_value'] - prev_aov) / prev_aov * 100
                )
            else:
                metrics['aov_growth_pct'] = None

        return metrics

    def calculate_monthly_trends(self) -> pd.DataFrame:
        """
        Calculate month-over-month trends.

        Returns:
            DataFrame with monthly metrics and growth rates
        """
        if 'month' not in self.sales_data.columns:
            raise ValueError("Month column not found in sales data")

        monthly = self.sales_data.groupby('month').agg({
            'price': 'sum',
            'order_id': 'nunique'
        }).reset_index()

        monthly.columns = ['month', 'revenue', 'orders']

        # Calculate month-over-month growth
        monthly['revenue_growth_pct'] = monthly['revenue'].pct_change() * 100
        monthly['orders_growth_pct'] = monthly['orders'].pct_change() * 100

        # Calculate average order value per month
        monthly['avg_order_value'] = monthly['revenue'] / monthly['orders']

        return monthly

    def analyze_product_performance(self) -> pd.DataFrame:
        """
        Analyze product category performance.

        Returns:
            DataFrame with category-level metrics sorted by revenue
        """
        if 'product_category_name' not in self.sales_data.columns:
            raise ValueError("Product category column not found in sales data")

        category_metrics = self.sales_data.groupby('product_category_name').agg({
            'price': 'sum',
            'order_id': 'nunique',
            'order_item_id': 'count'
        }).reset_index()

        category_metrics.columns = [
            'category',
            'revenue',
            'orders',
            'items_sold'
        ]

        # Calculate revenue share
        total_revenue = category_metrics['revenue'].sum()
        category_metrics['revenue_share_pct'] = (
            category_metrics['revenue'] / total_revenue * 100
        )

        # Calculate average order value by category
        category_metrics['avg_order_value'] = (
            category_metrics['revenue'] / category_metrics['orders']
        )

        # Sort by revenue
        category_metrics = category_metrics.sort_values('revenue', ascending=False)

        return category_metrics

    def analyze_geographic_performance(self) -> pd.DataFrame:
        """
        Analyze performance by geographic location (state).

        Returns:
            DataFrame with state-level metrics sorted by revenue
        """
        if 'customer_state' not in self.sales_data.columns:
            raise ValueError("Customer state column not found in sales data")

        state_metrics = self.sales_data.groupby('customer_state').agg({
            'price': 'sum',
            'order_id': 'nunique',
            'customer_id': 'nunique'
        }).reset_index()

        state_metrics.columns = [
            'state',
            'revenue',
            'orders',
            'customers'
        ]

        # Calculate revenue share
        total_revenue = state_metrics['revenue'].sum()
        state_metrics['revenue_share_pct'] = (
            state_metrics['revenue'] / total_revenue * 100
        )

        # Calculate average order value by state
        state_metrics['avg_order_value'] = (
            state_metrics['revenue'] / state_metrics['orders']
        )

        # Sort by revenue
        state_metrics = state_metrics.sort_values('revenue', ascending=False)

        return state_metrics

    def analyze_customer_satisfaction(self) -> Dict[str, any]:
        """
        Analyze customer satisfaction metrics from review scores.

        Returns:
            Dictionary containing satisfaction metrics
        """
        if 'review_score' not in self.sales_data.columns:
            return {"error": "Review score column not found"}

        # Get unique orders with their review scores (avoid duplicates)
        reviews = self.sales_data[['order_id', 'review_score']].drop_duplicates()

        metrics = {}
        metrics['avg_review_score'] = reviews['review_score'].mean()
        metrics['median_review_score'] = reviews['review_score'].median()
        metrics['total_reviews'] = len(reviews)

        # Distribution of scores
        score_dist = reviews['review_score'].value_counts(normalize=True).sort_index()
        metrics['score_distribution'] = score_dist.to_dict()

        # Calculate percentage of high satisfaction (scores 4 and 5)
        high_satisfaction = reviews[reviews['review_score'] >= 4]
        metrics['high_satisfaction_pct'] = (
            len(high_satisfaction) / len(reviews) * 100
        )

        return metrics

    def analyze_delivery_performance(self) -> Dict[str, any]:
        """
        Analyze delivery performance metrics.

        Returns:
            Dictionary containing delivery metrics
        """
        if 'delivery_days' not in self.sales_data.columns:
            return {"error": "Delivery days column not found"}

        # Get unique orders with delivery data
        delivery_data = self.sales_data[
            ['order_id', 'delivery_days', 'review_score']
        ].drop_duplicates()

        # Remove null delivery days
        delivery_data = delivery_data.dropna(subset=['delivery_days'])

        metrics = {}
        metrics['avg_delivery_days'] = delivery_data['delivery_days'].mean()
        metrics['median_delivery_days'] = delivery_data['delivery_days'].median()

        # Categorize delivery speed
        def categorize_delivery_speed(days):
            if pd.isna(days):
                return 'Unknown'
            if days <= 3:
                return '1-3 days'
            elif days <= 7:
                return '4-7 days'
            else:
                return '8+ days'

        delivery_data['delivery_category'] = delivery_data['delivery_days'].apply(
            categorize_delivery_speed
        )

        # Distribution of delivery categories
        category_dist = delivery_data['delivery_category'].value_counts(normalize=True)
        metrics['delivery_category_distribution'] = category_dist.to_dict()

        # Average review score by delivery category
        if 'review_score' in delivery_data.columns:
            review_by_delivery = delivery_data.groupby('delivery_category')[
                'review_score'
            ].mean().to_dict()
            metrics['avg_review_by_delivery_speed'] = review_by_delivery

        return metrics

    def generate_comprehensive_report(
        self,
        comparison_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, any]:
        """
        Generate a comprehensive report with all metrics.

        Args:
            comparison_data: Optional DataFrame for year-over-year comparison

        Returns:
            Dictionary containing all calculated metrics
        """
        report = {}

        report['revenue_metrics'] = self.calculate_revenue_metrics(comparison_data)

        try:
            report['monthly_trends'] = self.calculate_monthly_trends()
        except ValueError as e:
            report['monthly_trends'] = {"error": str(e)}

        try:
            report['product_performance'] = self.analyze_product_performance()
        except ValueError as e:
            report['product_performance'] = {"error": str(e)}

        try:
            report['geographic_performance'] = self.analyze_geographic_performance()
        except ValueError as e:
            report['geographic_performance'] = {"error": str(e)}

        report['customer_satisfaction'] = self.analyze_customer_satisfaction()
        report['delivery_performance'] = self.analyze_delivery_performance()

        return report


class MetricsVisualizer:
    """
    Creates visualizations for business metrics.
    """

    @staticmethod
    def plot_revenue_trend(
        monthly_data: pd.DataFrame,
        title: str = "Monthly Revenue Trend",
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Create a line plot of monthly revenue trend.

        Args:
            monthly_data: DataFrame with 'month' and 'revenue' columns
            title: Plot title
            figsize: Figure size

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(
            monthly_data['month'],
            monthly_data['revenue'],
            marker='o',
            linewidth=2,
            markersize=8,
            color='#2E86AB'
        )

        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Set x-axis to show all months
        ax.set_xticks(range(1, 13))
        ax.set_xlim(0.5, 12.5)

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_category_performance(
        category_data: pd.DataFrame,
        top_n: int = 10,
        title: str = "Top Product Categories by Revenue",
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Create a horizontal bar chart of product category performance.

        Args:
            category_data: DataFrame with 'category' and 'revenue' columns
            top_n: Number of top categories to display
            title: Plot title
            figsize: Figure size

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Get top N categories
        top_categories = category_data.head(top_n).sort_values('revenue')

        bars = ax.barh(
            top_categories['category'],
            top_categories['revenue'],
            color='#06A77D'
        )

        ax.set_xlabel('Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Product Category', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Format x-axis as currency
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f'${width:,.0f}',
                ha='left',
                va='center',
                fontsize=9,
                fontweight='bold'
            )

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_geographic_map(
        state_data: pd.DataFrame,
        title: str = "Revenue by State"
    ):
        """
        Create an interactive choropleth map of revenue by state.

        Args:
            state_data: DataFrame with 'state' and 'revenue' columns
            title: Plot title

        Returns:
            Plotly figure object
        """
        fig = px.choropleth(
            state_data,
            locations='state',
            color='revenue',
            locationmode='USA-states',
            scope='usa',
            title=title,
            color_continuous_scale='Reds',
            labels={'revenue': 'Revenue ($)'}
        )

        fig.update_layout(
            title_font_size=16,
            title_font_family='Arial',
            title_font_color='#333333',
            geo=dict(bgcolor='rgba(0,0,0,0)')
        )

        return fig

    @staticmethod
    def plot_review_distribution(
        review_data: pd.DataFrame,
        title: str = "Review Score Distribution",
        figsize: Tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """
        Create a horizontal bar chart of review score distribution.

        Args:
            review_data: DataFrame with 'order_id' and 'review_score' columns
            title: Plot title
            figsize: Figure size

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Get unique reviews
        reviews = review_data[['order_id', 'review_score']].drop_duplicates()

        # Calculate distribution
        score_dist = reviews['review_score'].value_counts(normalize=True).sort_index()

        bars = ax.barh(
            score_dist.index.astype(str),
            score_dist.values,
            color='#F18F01'
        )

        ax.set_xlabel('Percentage of Reviews', fontsize=12, fontweight='bold')
        ax.set_ylabel('Review Score', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Format x-axis as percentage
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*100:.1f}%'))

        # Add percentage labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f'{width*100:.1f}%',
                ha='left',
                va='center',
                fontsize=10,
                fontweight='bold'
            )

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_delivery_performance(
        delivery_data: pd.DataFrame,
        title: str = "Average Review Score by Delivery Speed",
        figsize: Tuple[int, int] = (10, 6)
    ) -> plt.Figure:
        """
        Create a bar chart showing review scores by delivery speed category.

        Args:
            delivery_data: DataFrame with 'delivery_days' and 'review_score' columns
            title: Plot title
            figsize: Figure size

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Get unique orders
        delivery_orders = delivery_data[
            ['order_id', 'delivery_days', 'review_score']
        ].drop_duplicates()

        # Categorize delivery speed
        def categorize_delivery_speed(days):
            if pd.isna(days):
                return 'Unknown'
            if days <= 3:
                return '1-3 days'
            elif days <= 7:
                return '4-7 days'
            else:
                return '8+ days'

        delivery_orders['delivery_category'] = delivery_orders['delivery_days'].apply(
            categorize_delivery_speed
        )

        # Calculate average review by category
        avg_by_category = delivery_orders.groupby('delivery_category')[
            'review_score'
        ].mean().sort_index()

        # Order categories properly
        category_order = ['1-3 days', '4-7 days', '8+ days']
        avg_by_category = avg_by_category.reindex(category_order)

        bars = ax.bar(
            avg_by_category.index,
            avg_by_category.values,
            color='#C73E1D'
        )

        ax.set_xlabel('Delivery Speed', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Review Score', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 5)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom',
                fontsize=11,
                fontweight='bold'
            )

        plt.tight_layout()
        return fig
