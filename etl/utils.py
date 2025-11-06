"""
ETL utility functions for OpsIntel360 platform
"""
import pandas as pd
import sqlite3
from pathlib import Path
from typing import Optional, List
import config


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        SQLite database connection
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    """
    Initialize the database with schema from SQL file.
    """
    schema_path = config.DATABASE_DIR / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    conn = get_db_connection()
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized at {config.DATABASE_PATH}")


def clean_dataframe(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Clean and standardize a DataFrame.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Convert date column to datetime
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values in numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    
    # Handle missing values in categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col != date_column and df[col].isnull().any():
            df[col] = df[col].fillna('Unknown')
    
    return df


def load_csv_to_db(csv_path: Path, table_name: str, 
                   if_exists: str = 'replace') -> int:
    """
    Load CSV data into database table.
    
    Args:
        csv_path: Path to CSV file
        table_name: Target database table name
        if_exists: How to behave if table exists ('fail', 'replace', 'append')
        
    Returns:
        Number of rows loaded
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read and clean data
    df = pd.read_csv(csv_path)
    df = clean_dataframe(df)
    
    # Load to database
    conn = get_db_connection()
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()
    
    return len(df)


def execute_query(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as DataFrame.
    
    Args:
        query: SQL query string
        params: Optional query parameters
        
    Returns:
        Query results as DataFrame
    """
    conn = get_db_connection()
    
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df


def get_latest_data(table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
    """
    Get the most recent data from a table.
    
    Args:
        table_name: Name of the table
        limit: Optional limit on number of rows
        
    Returns:
        DataFrame with latest data
    """
    query = f"SELECT * FROM {table_name} ORDER BY date DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    return execute_query(query)


def get_date_range_data(table_name: str, start_date: str, 
                        end_date: str) -> pd.DataFrame:
    """
    Get data within a specific date range.
    
    Args:
        table_name: Name of the table
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with filtered data
    """
    query = f"""
        SELECT * FROM {table_name}
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """
    
    return execute_query(query, (start_date, end_date))


def calculate_percentage_change(df: pd.DataFrame, column: str, 
                                periods: int = 1) -> pd.Series:
    """
    Calculate percentage change for a column.
    
    Args:
        df: Input DataFrame
        column: Column name to calculate change for
        periods: Number of periods to shift
        
    Returns:
        Series with percentage changes
    """
    return df[column].pct_change(periods=periods) * 100


def get_summary_statistics(table_name: str, 
                          numeric_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Get summary statistics for numeric columns in a table.
    
    Args:
        table_name: Name of the table
        numeric_columns: Optional list of specific columns
        
    Returns:
        DataFrame with summary statistics
    """
    df = execute_query(f"SELECT * FROM {table_name}")
    
    if numeric_columns:
        df = df[['date'] + numeric_columns]
    
    # Get numeric columns only
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    summary = numeric_df.describe().T
    summary['latest'] = numeric_df.iloc[-1] if len(numeric_df) > 0 else None
    
    return summary


def insert_insight(date: str, category: str, insight_text: str, 
                   severity: str = 'info', metric_value: Optional[float] = None) -> None:
    """
    Insert an insight/recommendation into the database.
    
    Args:
        date: Date of the insight
        category: Category (finance, sales, operations, hr, it)
        insight_text: The insight text
        severity: Severity level (info, warning, critical)
        metric_value: Optional associated metric value
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO insights (date, category, insight_text, severity, metric_value)
        VALUES (?, ?, ?, ?, ?)
    """, (date, category, insight_text, severity, metric_value))
    
    conn.commit()
    conn.close()


def insert_anomaly(date: str, metric_name: str, metric_value: float,
                   expected_value: Optional[float] = None,
                   anomaly_score: Optional[float] = None,
                   detection_method: str = 'unknown') -> None:
    """
    Insert an anomaly detection result into the database.
    
    Args:
        date: Date of the anomaly
        metric_name: Name of the metric
        metric_value: Actual value
        expected_value: Expected value
        anomaly_score: Anomaly score
        detection_method: Method used for detection
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO anomalies (date, metric_name, metric_value, expected_value, 
                              anomaly_score, detection_method)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, metric_name, metric_value, expected_value, anomaly_score, detection_method))
    
    conn.commit()
    conn.close()
