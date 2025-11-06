-- OpsIntel360 Database Schema
-- SQLite database for business analytics platform

-- Finance table
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    revenue REAL NOT NULL,
    expenses REAL NOT NULL,
    profit REAL NOT NULL,
    budget REAL,
    budget_variance_pct REAL,
    profit_margin_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

CREATE INDEX IF NOT EXISTS idx_finance_date ON finance(date);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    region TEXT NOT NULL,
    units_sold INTEGER NOT NULL,
    leads_generated INTEGER,
    conversion_rate_pct REAL,
    avg_deal_size REAL,
    total_revenue REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, region)
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);

-- Operations table
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    orders_processed INTEGER NOT NULL,
    avg_processing_time_hours REAL,
    ontime_delivery_pct REAL,
    downtime_hours REAL,
    defect_rate_pct REAL,
    operational_efficiency_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date);

-- HR table
CREATE TABLE IF NOT EXISTS hr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    employee_count INTEGER NOT NULL,
    new_hires INTEGER,
    terminations INTEGER,
    turnover_rate_pct REAL,
    absenteeism_rate_pct REAL,
    training_cost REAL,
    satisfaction_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

CREATE INDEX IF NOT EXISTS idx_hr_date ON hr(date);

-- IT Tickets table
CREATE TABLE IF NOT EXISTS it_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    priority TEXT NOT NULL,
    tickets_opened INTEGER NOT NULL,
    tickets_closed INTEGER NOT NULL,
    tickets_pending INTEGER,
    avg_resolution_time_hours REAL,
    first_response_time_hours REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, priority)
);

CREATE INDEX IF NOT EXISTS idx_tickets_date ON it_tickets(date);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON it_tickets(priority);

-- Insights/Recommendations table
CREATE TABLE IF NOT EXISTS insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    category TEXT NOT NULL,
    insight_text TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('info', 'warning', 'critical')),
    metric_value REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insights_date ON insights(date);
CREATE INDEX IF NOT EXISTS idx_insights_category ON insights(category);

-- Anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    expected_value REAL,
    anomaly_score REAL,
    detection_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anomalies_date ON anomalies(date);
CREATE INDEX IF NOT EXISTS idx_anomalies_metric ON anomalies(metric_name);

-- Forecasts table
CREATE TABLE IF NOT EXISTS forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    forecast_value REAL NOT NULL,
    lower_bound REAL,
    upper_bound REAL,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_date ON forecasts(date);
CREATE INDEX IF NOT EXISTS idx_forecasts_metric ON forecasts(metric_name);
