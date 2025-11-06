"""
Configuration settings for OpsIntel360 Platform
"""
import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"

# Database configuration
DATABASE_PATH = DATABASE_DIR / "opsintel.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Data generation parameters
DATA_CONFIG: Dict[str, Any] = {
    "start_date": "2023-01-01",
    "periods": 24,  # 24 months of data
    "freq": "M",  # Monthly frequency
}

# Forecasting configuration
FORECAST_CONFIG: Dict[str, Any] = {
    "forecast_periods": 6,  # Forecast 6 months ahead
    "yearly_seasonality": True,
    "weekly_seasonality": False,
    "daily_seasonality": False,
    "changepoint_prior_scale": 0.05,
    "seasonality_prior_scale": 10.0,
}

# Anomaly detection configuration
ANOMALY_CONFIG: Dict[str, Any] = {
    "contamination": 0.1,  # Expected proportion of outliers
    "z_score_threshold": 3,  # Standard deviations for z-score method
}

# Dashboard configuration
DASHBOARD_CONFIG: Dict[str, Any] = {
    "page_title": "OpsIntel360 - Business Operations Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Color scheme
COLORS: Dict[str, str] = {
    "primary": "#1e3a8a",  # Midnight blue
    "secondary": "#3b82f6",  # Bright blue
    "success": "#10b981",  # Green
    "warning": "#f59e0b",  # Amber
    "danger": "#ef4444",  # Red
    "background": "#f8fafc",  # Light gray
    "text": "#1e293b",  # Dark gray
}

# KPI thresholds for recommendations
KPI_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "revenue_growth": {"good": 5.0, "warning": 0.0, "critical": -5.0},
    "profit_margin": {"good": 20.0, "warning": 10.0, "critical": 5.0},
    "employee_turnover": {"good": 10.0, "warning": 15.0, "critical": 20.0},
    "ticket_resolution_hours": {"good": 24.0, "warning": 48.0, "critical": 72.0},
    "ontime_delivery": {"good": 95.0, "warning": 90.0, "critical": 85.0},
}

# API configuration
API_CONFIG: Dict[str, Any] = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
}

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
