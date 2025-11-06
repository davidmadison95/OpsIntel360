"""
OpsIntel360 - Main Streamlit Dashboard Application
Interactive business operations insights platform
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from etl.utils import (
    execute_query, get_latest_data, get_date_range_data,
    get_summary_statistics
)
from models.forecasting import TimeSeriesForecaster
from models.anomalies import AnomalyDetector
from models.insights import InsightEngine


# Page configuration
st.set_page_config(
    page_title=config.DASHBOARD_CONFIG['page_title'],
    page_icon=config.DASHBOARD_CONFIG['page_icon'],
    layout=config.DASHBOARD_CONFIG['layout'],
    initial_sidebar_state=config.DASHBOARD_CONFIG['initial_sidebar_state']
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    h1 {
        color: #1e3a8a;
    }
    h2 {
        color: #3b82f6;
    }
    .insight-critical {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .insight-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .insight-info {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def load_data():
    """Load all necessary data from database"""
    try:
        finance_df = execute_query("SELECT * FROM finance ORDER BY date")
        sales_df = execute_query("SELECT * FROM sales ORDER BY date")
        operations_df = execute_query("SELECT * FROM operations ORDER BY date")
        hr_df = execute_query("SELECT * FROM hr ORDER BY date")
        it_tickets_df = execute_query("SELECT * FROM it_tickets ORDER BY date")
        
        return finance_df, sales_df, operations_df, hr_df, it_tickets_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None


def create_kpi_card(label, value, delta=None, prefix="", suffix=""):
    """Create a styled KPI card"""
    delta_html = ""
    if delta is not None:
        delta_color = "#10b981" if delta >= 0 else "#ef4444"
        delta_symbol = "▲" if delta >= 0 else "▼"
        delta_html = f'<span style="color: {delta_color}; font-size: 14px;">{delta_symbol} {abs(delta):.1f}%</span>'
    
    card_html = f"""
    <div class="metric-card">
        <div style="font-size: 14px; color: #64748b; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 28px; font-weight: bold; color: #1e293b;">{prefix}{value:,.2f}{suffix}</div>
        {delta_html}
    </div>
    """
    return card_html


def render_kpi_overview(finance_df, sales_df, operations_df, hr_df, it_tickets_df):
    """Render KPI Overview tab"""
    st.header("📊 Key Performance Indicators")
    
    # Get latest values
    latest_finance = finance_df.iloc[-1]
    latest_ops = operations_df.iloc[-1]
    latest_hr = hr_df.iloc[-1]
    
    # Calculate deltas (MoM change)
    if len(finance_df) > 1:
        prev_finance = finance_df.iloc[-2]
        revenue_delta = ((latest_finance['revenue'] - prev_finance['revenue']) / prev_finance['revenue'] * 100)
        profit_delta = ((latest_finance['profit'] - prev_finance['profit']) / prev_finance['profit'] * 100)
    else:
        revenue_delta = None
        profit_delta = None
    
    # Top row KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card(
            "Revenue", 
            latest_finance['revenue'], 
            revenue_delta,
            prefix="$"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_kpi_card(
            "Profit", 
            latest_finance['profit'], 
            profit_delta,
            prefix="$"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_kpi_card(
            "Profit Margin", 
            latest_finance['profit_margin_pct'],
            suffix="%"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_kpi_card(
            "On-Time Delivery", 
            latest_ops['ontime_delivery_pct'],
            suffix="%"
        ), unsafe_allow_html=True)
    
    # Second row KPIs
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown(create_kpi_card(
            "Employee Count", 
            latest_hr['employee_count']
        ), unsafe_allow_html=True)
    
    with col6:
        st.markdown(create_kpi_card(
            "Turnover Rate", 
            latest_hr['turnover_rate_pct'],
            suffix="%"
        ), unsafe_allow_html=True)
    
    with col7:
        # Calculate total IT tickets
        latest_tickets = it_tickets_df[it_tickets_df['date'] == it_tickets_df['date'].max()]
        total_tickets = latest_tickets['tickets_opened'].sum()
        st.markdown(create_kpi_card(
            "IT Tickets (Month)", 
            total_tickets
        ), unsafe_allow_html=True)
    
    with col8:
        st.markdown(create_kpi_card(
            "Satisfaction Score", 
            latest_hr['satisfaction_score'],
            suffix="/10"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Revenue and Profit Trend Chart
    st.subheader("Financial Performance Trends")
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Revenue & Expenses Over Time", "Profit Margin Trend")
    )
    
    fig.add_trace(
        go.Scatter(x=finance_df['date'], y=finance_df['revenue'], 
                   name="Revenue", line=dict(color='#3b82f6', width=3)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=finance_df['date'], y=finance_df['expenses'], 
                   name="Expenses", line=dict(color='#ef4444', width=3)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=finance_df['date'], y=finance_df['profit_margin_pct'], 
                   name="Profit Margin %", line=dict(color='#10b981', width=3),
                   fill='tozeroy'),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig.update_yaxes(title_text="Profit Margin (%)", row=1, col=2)
    
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional Sales Performance
    st.subheader("Regional Sales Performance")
    
    sales_by_region = sales_df.groupby('region').agg({
        'units_sold': 'sum',
        'total_revenue': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_units = px.bar(
            sales_by_region, x='region', y='units_sold',
            title="Units Sold by Region",
            color='units_sold',
            color_continuous_scale='Blues'
        )
        fig_units.update_layout(showlegend=False)
        st.plotly_chart(fig_units, use_container_width=True)
    
    with col2:
        fig_revenue = px.pie(
            sales_by_region, values='total_revenue', names='region',
            title="Revenue Distribution by Region"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)


def render_forecasting_tab(finance_df):
    """Render Forecasting & Trends tab"""
    st.header("🔮 Forecasting & Trends")
    
    # Metric selection
    metric_options = {
        'Revenue': ('revenue', '$'),
        'Expenses': ('expenses', '$'),
        'Profit': ('profit', '$'),
        'Profit Margin': ('profit_margin_pct', '%')
    }
    
    selected_metric_name = st.selectbox(
        "Select Metric to Forecast",
        list(metric_options.keys())
    )
    
    metric_col, unit = metric_options[selected_metric_name]
    
    # Forecast periods slider
    forecast_months = st.slider(
        "Forecast Horizon (months)",
        min_value=3,
        max_value=12,
        value=6
    )
    
    with st.spinner("Generating forecast..."):
        try:
            # Prepare data for Prophet
            prophet_df = finance_df[['date', metric_col]].copy()
            prophet_df.columns = ['ds', 'y']
            prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
            
            # Train and forecast
            forecaster = TimeSeriesForecaster()
            model = forecaster.train_model(prophet_df, selected_metric_name)
            forecast = forecaster.generate_forecast(model, forecast_months, freq='M')
            
            # Calculate accuracy
            accuracy = forecaster._calculate_accuracy(prophet_df, forecast)
            
            # Display accuracy metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("RMSE", f"{accuracy['rmse']:,.2f}")
            with col2:
                st.metric("MAE", f"{accuracy['mae']:,.2f}")
            with col3:
                st.metric("MAPE", f"{accuracy['mape']:.2f}%")
            
            # Create forecast visualization
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=prophet_df['ds'],
                y=prophet_df['y'],
                name='Historical',
                line=dict(color='#3b82f6', width=2)
            ))
            
            # Forecast
            future_forecast = forecast[forecast['ds'] > prophet_df['ds'].max()]
            
            fig.add_trace(go.Scatter(
                x=future_forecast['ds'],
                y=future_forecast['yhat'],
                name='Forecast',
                line=dict(color='#10b981', width=2, dash='dash')
            ))
            
            # Confidence intervals
            fig.add_trace(go.Scatter(
                x=future_forecast['ds'],
                y=future_forecast['yhat_upper'],
                fill=None,
                mode='lines',
                line_color='rgba(16, 185, 129, 0)',
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=future_forecast['ds'],
                y=future_forecast['yhat_lower'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(16, 185, 129, 0)',
                fillcolor='rgba(16, 185, 129, 0.2)',
                name='Confidence Interval'
            ))
            
            fig.update_layout(
                title=f"{selected_metric_name} Forecast - Next {forecast_months} Months",
                xaxis_title="Date",
                yaxis_title=f"{selected_metric_name} ({unit})",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.subheader("Forecast Values")
            forecast_table = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast_table.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound']
            forecast_table['Date'] = forecast_table['Date'].dt.strftime('%Y-%m')
            
            st.dataframe(
                forecast_table.style.format({
                    'Forecast': f'{{:.2f}}{unit}',
                    'Lower Bound': f'{{:.2f}}{unit}',
                    'Upper Bound': f'{{:.2f}}{unit}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"Error generating forecast: {e}")


def render_anomalies_tab():
    """Render Anomalies Detection tab"""
    st.header("⚠️ Anomaly Detection")
    
    with st.spinner("Detecting anomalies..."):
        try:
            detector = AnomalyDetector()
            anomalies = detector.detect_all_anomalies()
            
            if not anomalies:
                st.success("✅ No significant anomalies detected in recent data!")
                return
            
            # Summary metrics
            total_anomalies = sum(len(df) for df in anomalies.values())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Anomalies Detected", total_anomalies)
            with col2:
                st.metric("Metrics Analyzed", len(anomalies))
            
            st.markdown("---")
            
            # Anomalies by metric
            for metric_name, anomaly_df in anomalies.items():
                with st.expander(f"🔍 {metric_name} - {len(anomaly_df)} anomalies", expanded=True):
                    # Get the actual metric column name
                    metric_col = anomaly_df['metric_name'].iloc[0]
                    
                    # Create chart
                    fig = go.Figure()
                    
                    # Get full historical data for context
                    table_name = anomaly_df['table_name'].iloc[0]
                    full_data = execute_query(
                        f"SELECT date, {metric_col} FROM {table_name} ORDER BY date"
                    )
                    
                    # Plot all data
                    fig.add_trace(go.Scatter(
                        x=full_data['date'],
                        y=full_data[metric_col],
                        name='Normal',
                        line=dict(color='#3b82f6', width=2)
                    ))
                    
                    # Highlight anomalies
                    fig.add_trace(go.Scatter(
                        x=anomaly_df['date'],
                        y=anomaly_df[metric_col],
                        name='Anomaly',
                        mode='markers',
                        marker=dict(color='#ef4444', size=12, symbol='x')
                    ))
                    
                    fig.update_layout(
                        title=f"{metric_name} with Anomalies Highlighted",
                        xaxis_title="Date",
                        yaxis_title=metric_name,
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Anomaly details table
                    display_df = anomaly_df[['date', metric_col, 'z_score']].copy()
                    display_df.columns = ['Date', 'Value', 'Z-Score']
                    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
                    
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Generate insights
                    insights = detector.generate_anomaly_insights(anomaly_df, metric_name)
                    for insight in insights:
                        st.warning(insight)
            
        except Exception as e:
            st.error(f"Error detecting anomalies: {e}")


def render_recommendations_tab():
    """Render AI-Generated Recommendations tab"""
    st.header("💡 AI-Generated Insights & Recommendations")
    
    with st.spinner("Generating insights..."):
        try:
            engine = InsightEngine()
            insights = engine.generate_all_insights()
            
            if not insights:
                st.info("No new insights generated. Check back after more data is collected.")
                return
            
            # Filter controls
            col1, col2 = st.columns(2)
            
            with col1:
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    ['critical', 'warning', 'info'],
                    default=['critical', 'warning', 'info']
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Filter by Category",
                    ['finance', 'sales', 'operations', 'hr', 'it'],
                    default=['finance', 'sales', 'operations', 'hr', 'it']
                )
            
            # Filter insights
            filtered_insights = [
                i for i in insights 
                if i['severity'] in severity_filter and i['category'] in category_filter
            ]
            
            st.markdown(f"**Showing {len(filtered_insights)} of {len(insights)} insights**")
            st.markdown("---")
            
            # Display insights by severity
            for severity in ['critical', 'warning', 'info']:
                severity_insights = [i for i in filtered_insights if i['severity'] == severity]
                
                if not severity_insights:
                    continue
                
                severity_label = {
                    'critical': '🔴 Critical',
                    'warning': '⚠️ Warning',
                    'info': '✅ Info'
                }[severity]
                
                st.subheader(f"{severity_label} ({len(severity_insights)})")
                
                for insight in severity_insights:
                    css_class = f"insight-{severity}"
                    
                    insight_html = f"""
                    <div class="{css_class}">
                        <strong>{insight['category'].upper()}</strong> | {insight['date']}<br>
                        {insight['insight_text']}
                    </div>
                    """
                    st.markdown(insight_html, unsafe_allow_html=True)
            
            # Export functionality
            st.markdown("---")
            if st.button("📥 Export Insights to JSON"):
                insights_json = json.dumps(insights, indent=2)
                st.download_button(
                    label="Download Insights",
                    data=insights_json,
                    file_name=f"opsintel360_insights_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
        except Exception as e:
            st.error(f"Error generating insights: {e}")


def main():
    """Main dashboard application"""
    # Header
    st.title("📊 OpsIntel360")
    st.markdown("**Business Operations Insights Dashboard**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1e3a8a/ffffff?text=OpsIntel360", 
                 use_container_width=True)
        st.markdown("### Dashboard Controls")
        
        # Date range filter
        st.markdown("#### Date Range")
        date_option = st.radio(
            "Select Period",
            ["Last 6 Months", "Last 12 Months", "All Time", "Custom"],
            index=1
        )
        
        if date_option == "Custom":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        st.markdown("---")
        
        # Refresh data button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Data Last Updated:**")
        st.markdown(f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # Load data
    with st.spinner("Loading data..."):
        finance_df, sales_df, operations_df, hr_df, it_tickets_df = load_data()
    
    if finance_df is None:
        st.error("❌ Could not load data. Please run the ETL pipeline first.")
        st.code("python etl/etl_pipeline.py", language="bash")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 KPI Overview",
        "🔮 Forecasting & Trends",
        "⚠️ Anomalies",
        "💡 Recommendations"
    ])
    
    with tab1:
        render_kpi_overview(finance_df, sales_df, operations_df, hr_df, it_tickets_df)
    
    with tab2:
        render_forecasting_tab(finance_df)
    
    with tab3:
        render_anomalies_tab()
    
    with tab4:
        render_recommendations_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #64748b;'>"
        "OpsIntel360 © 2024 | Developed by David Madison"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
