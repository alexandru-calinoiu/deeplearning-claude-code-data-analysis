"""
E-Commerce Business Analytics Dashboard

A professional Streamlit dashboard for visualizing e-commerce business metrics
including revenue trends, product performance, geographic distribution, and
customer satisfaction.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from data_loader import load_and_process_data
from business_metrics import BusinessMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container */
    .main > div {
        padding-top: 2rem;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1rem;
    }

    /* Card styling */
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }

    /* Header styling */
    h1 {
        color: #1f2937;
        font-weight: 700;
    }

    /* Chart containers */
    .chart-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 400px;
    }

    /* Bottom cards */
    .bottom-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 200px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(data_path='ecommerce_data/'):
    """Load and process e-commerce data with caching."""
    loader, processed_data = load_and_process_data(data_path)
    return loader, processed_data


@st.cache_data
def get_available_years(_loader):
    """Get list of available years from the data."""
    summary = _loader.get_data_summary()
    return summary.get('years_available', [2023])


def format_currency(value):
    """Format large numbers as currency with K/M suffixes."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def format_number(value):
    """Format large numbers with K/M suffixes."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:.0f}"


def create_revenue_trend_chart(current_monthly, previous_monthly, current_year, previous_year):
    """Create revenue trend line chart with current and previous period."""
    fig = go.Figure()

    # Previous period (dashed line) - only if data exists
    if previous_monthly is not None and len(previous_monthly) > 0:
        fig.add_trace(go.Scatter(
            x=previous_monthly['month'],
            y=previous_monthly['revenue'],
            mode='lines',
            name=f'{previous_year}',
            line=dict(color='#93C5FD', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
        ))

    # Current period (solid line)
    fig.add_trace(go.Scatter(
        x=current_monthly['month'],
        y=current_monthly['revenue'],
        mode='lines+markers',
        name=f'{current_year}',
        line=dict(color='#2563EB', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title="Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            tickmode='linear',
            tick0=1,
            dtick=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E5E7EB',
            tickformat='$,.0s'
        )
    )

    return fig


def create_category_chart(product_performance):
    """Create top 10 categories bar chart with blue gradient."""
    top_10 = product_performance.head(10).sort_values('revenue', ascending=True)

    # Create color gradient (lighter for lower values)
    colors = [f'rgba(37, 99, 235, {0.4 + (i/10)*0.6})' for i in range(len(top_10))]

    fig = go.Figure(go.Bar(
        x=top_10['revenue'],
        y=top_10['category'],
        orientation='h',
        marker=dict(color=colors),
        text=[format_currency(v) for v in top_10['revenue']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title="Top 10 Product Categories",
        xaxis_title="Revenue",
        yaxis_title="",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickformat='$,.0s'
        ),
        yaxis=dict(
            showgrid=False
        )
    )

    return fig


def create_geographic_map(geo_performance):
    """Create US choropleth map with blue gradient."""
    fig = px.choropleth(
        geo_performance,
        locations='state',
        color='revenue',
        locationmode='USA-states',
        scope='usa',
        color_continuous_scale='Blues',
        labels={'revenue': 'Revenue'}
    )

    fig.update_layout(
        title="Revenue by State",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )

    return fig


def create_satisfaction_delivery_chart(sales_data):
    """Create bar chart showing satisfaction vs delivery time."""
    # Get unique orders
    delivery_orders = sales_data[
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
    ].mean().reset_index()

    # Order categories properly
    category_order = ['1-3 days', '4-7 days', '8+ days']
    avg_by_category = avg_by_category.set_index('delivery_category').reindex(category_order).reset_index()

    fig = go.Figure(go.Bar(
        x=avg_by_category['delivery_category'],
        y=avg_by_category['review_score'],
        marker=dict(color='#2563EB'),
        text=[f'{v:.2f}' for v in avg_by_category['review_score']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Avg Review: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Average Review Score by Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        plot_bgcolor='white',
        yaxis=dict(
            range=[0, 5],
            showgrid=True,
            gridcolor='#E5E7EB'
        ),
        xaxis=dict(
            showgrid=False
        )
    )

    return fig


def main():
    # Load data
    loader, processed_data = load_data()
    available_years = get_available_years(loader)

    # Header with title and date range filter
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("E-Commerce Business Analytics Dashboard")
    with col2:
        # Set default year to 2023 if available
        sorted_years = sorted(available_years, reverse=True)
        default_index = sorted_years.index(2023) if 2023 in sorted_years else 0

        selected_year = st.selectbox(
            "Select Year",
            options=sorted_years,
            index=default_index
        )
    with col3:
        selected_month = st.selectbox(
            "Select Month",
            options=["All Months"] + [f"{i:02d} - {month}" for i, month in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ], 1)],
            index=0
        )

        # Convert month selection to filter value
        month_filter = None if selected_month == "All Months" else int(selected_month.split(" - ")[0])

    # Calculate comparison year
    comparison_year = selected_year - 1

    # Create datasets
    sales_current = loader.create_sales_dataset(
        year_filter=selected_year,
        month_filter=month_filter,
        status_filter='delivered'
    )

    # Check if comparison year has data
    sales_comparison = None
    if comparison_year in available_years:
        sales_comparison = loader.create_sales_dataset(
            year_filter=comparison_year,
            month_filter=month_filter,
            status_filter='delivered'
        )

    # Calculate metrics
    calculator = BusinessMetricsCalculator(sales_current)

    revenue_metrics = calculator.calculate_revenue_metrics(comparison_data=sales_comparison)
    product_performance = calculator.analyze_product_performance()
    geo_performance = calculator.analyze_geographic_performance()
    delivery_metrics = calculator.analyze_delivery_performance()
    satisfaction_metrics = calculator.analyze_customer_satisfaction()

    # Monthly trends (only for full year analysis)
    monthly_trends = None
    monthly_trends_prev = None
    if month_filter is None:
        try:
            monthly_trends = calculator.calculate_monthly_trends()
            if sales_comparison is not None and len(sales_comparison) > 0:
                calculator_comparison = BusinessMetricsCalculator(sales_comparison)
                monthly_trends_prev = calculator_comparison.calculate_monthly_trends()
        except:
            pass

    # Previous year delivery metrics
    delivery_metrics_prev = None
    if sales_comparison is not None and len(sales_comparison) > 0:
        calculator_comparison = BusinessMetricsCalculator(sales_comparison)
        delivery_metrics_prev = calculator_comparison.analyze_delivery_performance()

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI Row - 4 cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        trend_value = revenue_metrics.get('revenue_growth_pct')
        st.metric(
            label="Total Revenue",
            value=format_currency(revenue_metrics['total_revenue']),
            delta=f"{trend_value:.2f}%" if trend_value is not None else None,
            delta_color="normal" if (trend_value is not None and trend_value >= 0) else "inverse"
        )

    with kpi_col2:
        # Monthly growth - average MoM growth
        if monthly_trends is not None and len(monthly_trends) > 0:
            avg_monthly_growth = monthly_trends['revenue_growth_pct'].mean()
            if pd.notna(avg_monthly_growth):
                st.metric(
                    label="Monthly Growth",
                    value=f"{avg_monthly_growth:.2f}%"
                )
            else:
                st.metric(label="Monthly Growth", value="N/A")
        else:
            st.metric(label="Monthly Growth", value="N/A")

    with kpi_col3:
        aov_trend = revenue_metrics.get('aov_growth_pct')
        st.metric(
            label="Average Order Value",
            value=format_currency(revenue_metrics['average_order_value']),
            delta=f"{aov_trend:.2f}%" if aov_trend is not None else None,
            delta_color="normal" if (aov_trend is not None and aov_trend >= 0) else "inverse"
        )

    with kpi_col4:
        order_trend = revenue_metrics.get('order_growth_pct')
        st.metric(
            label="Total Orders",
            value=format_number(revenue_metrics['total_orders']),
            delta=f"{order_trend:.2f}%" if order_trend is not None else None,
            delta_color="normal" if (order_trend is not None and order_trend >= 0) else "inverse"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Grid - 2x2 layout
    chart_row1_col1, chart_row1_col2 = st.columns(2)

    with chart_row1_col1:
        if monthly_trends is not None and len(monthly_trends) > 0:
            revenue_chart = create_revenue_trend_chart(
                monthly_trends, monthly_trends_prev, selected_year, comparison_year
            )
            st.plotly_chart(revenue_chart, use_container_width=True)
        else:
            st.info("Revenue trend chart is only available for full year analysis. Please select 'All Months'.")

    with chart_row1_col2:
        category_chart = create_category_chart(product_performance)
        st.plotly_chart(category_chart, use_container_width=True)

    chart_row2_col1, chart_row2_col2 = st.columns(2)

    with chart_row2_col1:
        geo_chart = create_geographic_map(geo_performance)
        st.plotly_chart(geo_chart, use_container_width=True)

    with chart_row2_col2:
        satisfaction_chart = create_satisfaction_delivery_chart(sales_current)
        st.plotly_chart(satisfaction_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Row - 2 cards
    bottom_col1, bottom_col2 = st.columns(2)

    with bottom_col1:
        # Calculate delivery time trend
        current_delivery = delivery_metrics['avg_delivery_days']
        delivery_trend_pct = None

        if delivery_metrics_prev is not None:
            prev_delivery = delivery_metrics_prev.get('avg_delivery_days')
            if prev_delivery is not None and prev_delivery > 0:
                delivery_trend_pct = ((current_delivery - prev_delivery) / prev_delivery * 100)

        st.metric(
            label="Average Delivery Time",
            value=f"{current_delivery:.1f} days",
            delta=f"{delivery_trend_pct:.2f}%" if delivery_trend_pct is not None else None,
            delta_color="inverse" if (delivery_trend_pct is not None and delivery_trend_pct >= 0) else "normal"  # Lower is better
        )

    with bottom_col2:
        avg_score = satisfaction_metrics['avg_review_score']
        # Display stars
        full_stars = int(avg_score)
        stars_display = "⭐" * full_stars
        if avg_score - full_stars >= 0.5:
            stars_display += "⭐"

        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 3rem; font-weight: 600; color: #1f2937;'>{avg_score:.2f}</div>
            <div style='font-size: 2rem; margin: 0.5rem 0;'>{stars_display}</div>
            <div style='font-size: 1rem; color: #6b7280;'>Average Review Score</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
