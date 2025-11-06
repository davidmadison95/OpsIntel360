"""
Data generation script for OpsIntel360 platform
Generates realistic synthetic business data across 5 domains
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple
import config

np.random.seed(42)


def generate_finance_data(start_date: str, periods: int) -> pd.DataFrame:
    """
    Generate financial data with revenue, expenses, profit, and budget variance.
    
    Args:
        start_date: Starting date for data generation
        periods: Number of periods (months) to generate
        
    Returns:
        DataFrame with financial metrics
    """
    dates = pd.date_range(start=start_date, periods=periods, freq='M')
    
    # Base revenue with growth trend and seasonality
    base_revenue = 500000
    growth_rate = 0.03  # 3% monthly growth
    revenue = []
    
    for i in range(periods):
        trend = base_revenue * (1 + growth_rate) ** i
        seasonality = np.sin(i * 2 * np.pi / 12) * 50000  # Yearly seasonality
        noise = np.random.normal(0, 20000)
        revenue.append(max(0, trend + seasonality + noise))
    
    # Expenses are correlated with revenue but with different patterns
    expenses = [r * np.random.uniform(0.65, 0.75) + np.random.normal(0, 15000) 
                for r in revenue]
    
    # Profit calculation
    profit = [r - e for r, e in zip(revenue, expenses)]
    
    # Budget variance (actual vs budget)
    budget = [r * np.random.uniform(0.95, 1.05) for r in revenue]
    budget_variance = [(r - b) / b * 100 for r, b in zip(revenue, budget)]
    
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'expenses': expenses,
        'profit': profit,
        'budget': budget,
        'budget_variance_pct': budget_variance,
        'profit_margin_pct': [(p / r * 100) if r > 0 else 0 
                               for p, r in zip(profit, revenue)]
    })
    
    return df


def generate_sales_data(start_date: str, periods: int) -> pd.DataFrame:
    """
    Generate sales data with units sold, conversion rates, and regional performance.
    
    Args:
        start_date: Starting date for data generation
        periods: Number of periods to generate
        
    Returns:
        DataFrame with sales metrics
    """
    dates = pd.date_range(start=start_date, periods=periods, freq='M')
    regions = ['North', 'South', 'East', 'West']
    
    data = []
    for date in dates:
        for region in regions:
            # Region-specific patterns
            region_multiplier = {
                'North': 1.2, 'South': 0.9, 'East': 1.1, 'West': 1.0
            }[region]
            
            units_sold = int(np.random.normal(
                1000 * region_multiplier, 150
            ))
            
            conversion_rate = np.random.uniform(0.15, 0.35) * region_multiplier
            avg_deal_size = np.random.normal(5000, 500)
            leads_generated = int(units_sold / max(conversion_rate, 0.01))
            
            data.append({
                'date': date,
                'region': region,
                'units_sold': max(0, units_sold),
                'leads_generated': max(0, leads_generated),
                'conversion_rate_pct': round(conversion_rate * 100, 2),
                'avg_deal_size': round(max(1000, avg_deal_size), 2),
                'total_revenue': round(max(0, units_sold * avg_deal_size), 2)
            })
    
    return pd.DataFrame(data)


def generate_operations_data(start_date: str, periods: int) -> pd.DataFrame:
    """
    Generate operations data with order processing and delivery metrics.
    
    Args:
        start_date: Starting date for data generation
        periods: Number of periods to generate
        
    Returns:
        DataFrame with operations metrics
    """
    dates = pd.date_range(start=start_date, periods=periods, freq='M')
    
    data = []
    for i, date in enumerate(dates):
        # Gradual improvement over time
        improvement_factor = 1 - (i * 0.01)
        
        orders_processed = int(np.random.normal(3500, 300))
        processing_time_hours = max(1, np.random.normal(
            48 * improvement_factor, 8
        ))
        
        ontime_delivery_pct = min(100, max(70, np.random.normal(
            90 + (i * 0.3), 5
        )))
        
        downtime_hours = max(0, np.random.exponential(4) * improvement_factor)
        
        defect_rate_pct = max(0, min(10, np.random.normal(
            3 * improvement_factor, 1
        )))
        
        data.append({
            'date': date,
            'orders_processed': orders_processed,
            'avg_processing_time_hours': round(processing_time_hours, 2),
            'ontime_delivery_pct': round(ontime_delivery_pct, 2),
            'downtime_hours': round(downtime_hours, 2),
            'defect_rate_pct': round(defect_rate_pct, 2),
            'operational_efficiency_pct': round(
                (ontime_delivery_pct + (100 - defect_rate_pct)) / 2, 2
            )
        })
    
    return pd.DataFrame(data)


def generate_hr_data(start_date: str, periods: int) -> pd.DataFrame:
    """
    Generate HR data with employee counts, turnover, and training metrics.
    
    Args:
        start_date: Starting date for data generation
        periods: Number of periods to generate
        
    Returns:
        DataFrame with HR metrics
    """
    dates = pd.date_range(start=start_date, periods=periods, freq='M')
    
    base_employees = 250
    data = []
    
    for i, date in enumerate(dates):
        # Gradual growth with some volatility
        employee_count = int(base_employees + (i * 2) + np.random.normal(0, 5))
        
        # Seasonal turnover patterns
        turnover_rate = max(0, min(25, np.random.normal(
            12 + np.sin(i * 2 * np.pi / 12) * 3, 2
        )))
        
        absenteeism_rate = max(0, min(10, np.random.normal(3.5, 1)))
        
        training_cost = employee_count * np.random.uniform(200, 400)
        
        satisfaction_score = min(10, max(5, np.random.normal(7.5, 0.8)))
        
        data.append({
            'date': date,
            'employee_count': employee_count,
            'new_hires': int(max(0, np.random.poisson(5))),
            'terminations': int(max(0, np.random.poisson(3))),
            'turnover_rate_pct': round(turnover_rate, 2),
            'absenteeism_rate_pct': round(absenteeism_rate, 2),
            'training_cost': round(training_cost, 2),
            'satisfaction_score': round(satisfaction_score, 2)
        })
    
    return pd.DataFrame(data)


def generate_it_tickets_data(start_date: str, periods: int) -> pd.DataFrame:
    """
    Generate IT support tickets data with resolution times and priorities.
    
    Args:
        start_date: Starting date for data generation
        periods: Number of periods to generate
        
    Returns:
        DataFrame with IT ticket metrics
    """
    dates = pd.date_range(start=start_date, periods=periods, freq='M')
    priorities = ['Critical', 'High', 'Medium', 'Low']
    
    data = []
    for i, date in enumerate(dates):
        # Improvement in resolution time over time
        improvement = 1 - (i * 0.015)
        
        for priority in priorities:
            # Priority-specific patterns
            priority_multiplier = {
                'Critical': 0.1, 'High': 0.25, 'Medium': 0.4, 'Low': 0.25
            }[priority]
            
            tickets_opened = int(np.random.poisson(
                300 * priority_multiplier
            ))
            
            tickets_closed = int(tickets_opened * np.random.uniform(0.85, 1.1))
            
            resolution_time_map = {
                'Critical': 4, 'High': 16, 'Medium': 40, 'Low': 72
            }
            base_resolution = resolution_time_map[priority]
            
            avg_resolution_hours = max(1, np.random.normal(
                base_resolution * improvement, base_resolution * 0.3
            ))
            
            data.append({
                'date': date,
                'priority': priority,
                'tickets_opened': tickets_opened,
                'tickets_closed': tickets_closed,
                'tickets_pending': max(0, tickets_opened - tickets_closed),
                'avg_resolution_time_hours': round(avg_resolution_hours, 2),
                'first_response_time_hours': round(avg_resolution_hours * 0.2, 2)
            })
    
    return pd.DataFrame(data)


def generate_all_data() -> Tuple[pd.DataFrame, ...]:
    """
    Generate all synthetic datasets and save to CSV files.
    
    Returns:
        Tuple of DataFrames (finance, sales, operations, hr, it_tickets)
    """
    print("Generating synthetic business data...")
    
    start_date = config.DATA_CONFIG["start_date"]
    periods = config.DATA_CONFIG["periods"]
    
    # Generate all datasets
    finance_df = generate_finance_data(start_date, periods)
    sales_df = generate_sales_data(start_date, periods)
    operations_df = generate_operations_data(start_date, periods)
    hr_df = generate_hr_data(start_date, periods)
    it_tickets_df = generate_it_tickets_data(start_date, periods)
    
    # Save to CSV files
    data_dir = config.DATA_DIR
    
    finance_df.to_csv(data_dir / 'finance.csv', index=False)
    sales_df.to_csv(data_dir / 'sales.csv', index=False)
    operations_df.to_csv(data_dir / 'operations.csv', index=False)
    hr_df.to_csv(data_dir / 'hr.csv', index=False)
    it_tickets_df.to_csv(data_dir / 'it_tickets.csv', index=False)
    
    print(f"✓ Finance data: {len(finance_df)} records")
    print(f"✓ Sales data: {len(sales_df)} records")
    print(f"✓ Operations data: {len(operations_df)} records")
    print(f"✓ HR data: {len(hr_df)} records")
    print(f"✓ IT Tickets data: {len(it_tickets_df)} records")
    print(f"\nAll data saved to {data_dir}")
    
    return finance_df, sales_df, operations_df, hr_df, it_tickets_df


if __name__ == "__main__":
    generate_all_data()
