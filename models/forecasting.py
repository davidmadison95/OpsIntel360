"""
Time-series forecasting module using Facebook Prophet
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

import config
from etl.utils import execute_query, get_db_connection


class TimeSeriesForecaster:
    """
    Time-series forecasting using Facebook Prophet
    """
    
    def __init__(self):
        """Initialize forecaster with configuration"""
        self.forecast_config = config.FORECAST_CONFIG
        self.models: Dict[str, Prophet] = {}
        self.forecasts: Dict[str, pd.DataFrame] = {}
        
    def prepare_data(self, df: pd.DataFrame, date_col: str, 
                     value_col: str) -> pd.DataFrame:
        """
        Prepare data for Prophet (requires 'ds' and 'y' columns).
        
        Args:
            df: Input DataFrame
            date_col: Name of date column
            value_col: Name of value column
            
        Returns:
            DataFrame formatted for Prophet
        """
        prophet_df = df[[date_col, value_col]].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        prophet_df = prophet_df.sort_values('ds')
        prophet_df = prophet_df.dropna()
        
        return prophet_df
    
    def train_model(self, df: pd.DataFrame, metric_name: str,
                   custom_params: Optional[Dict] = None) -> Prophet:
        """
        Train a Prophet model on historical data.
        
        Args:
            df: DataFrame with 'ds' and 'y' columns
            metric_name: Name of the metric being forecasted
            custom_params: Optional custom parameters for Prophet
            
        Returns:
            Trained Prophet model
        """
        # Merge default config with custom params
        params = {
            'yearly_seasonality': self.forecast_config['yearly_seasonality'],
            'weekly_seasonality': self.forecast_config['weekly_seasonality'],
            'daily_seasonality': self.forecast_config['daily_seasonality'],
            'changepoint_prior_scale': self.forecast_config['changepoint_prior_scale'],
            'seasonality_prior_scale': self.forecast_config['seasonality_prior_scale'],
        }
        
        if custom_params:
            params.update(custom_params)
        
        # Initialize and train model
        model = Prophet(**params)
        model.fit(df)
        
        # Store model
        self.models[metric_name] = model
        
        return model
    
    def generate_forecast(self, model: Prophet, periods: int,
                         freq: str = 'M') -> pd.DataFrame:
        """
        Generate future predictions using trained model.
        
        Args:
            model: Trained Prophet model
            periods: Number of periods to forecast
            freq: Frequency ('D', 'M', 'Y')
            
        Returns:
            DataFrame with forecast
        """
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        
        return forecast
    
    def forecast_metric(self, table_name: str, date_col: str,
                       value_col: str, metric_name: str,
                       periods: Optional[int] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete forecasting pipeline for a single metric.
        
        Args:
            table_name: Database table name
            date_col: Date column name
            value_col: Value column name
            metric_name: Name for the metric
            periods: Number of periods to forecast (default from config)
            
        Returns:
            Tuple of (forecast DataFrame, accuracy metrics)
        """
        if periods is None:
            periods = self.forecast_config['forecast_periods']
        
        # Get historical data
        query = f"SELECT {date_col}, {value_col} FROM {table_name} ORDER BY {date_col}"
        df = execute_query(query)
        
        # Prepare data
        prophet_df = self.prepare_data(df, date_col, value_col)
        
        # Train model
        model = self.train_model(prophet_df, metric_name)
        
        # Generate forecast
        forecast = self.generate_forecast(model, periods)
        
        # Calculate accuracy metrics on historical data
        metrics = self._calculate_accuracy(prophet_df, forecast)
        
        # Store forecast
        self.forecasts[metric_name] = forecast
        
        return forecast, metrics
    
    def _calculate_accuracy(self, actual_df: pd.DataFrame, 
                          forecast_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate forecast accuracy metrics.
        
        Args:
            actual_df: Actual data with 'ds' and 'y'
            forecast_df: Forecast data with 'ds' and 'yhat'
            
        Returns:
            Dictionary of accuracy metrics
        """
        # Merge actual and predicted
        merged = actual_df.merge(
            forecast_df[['ds', 'yhat']], 
            on='ds', 
            how='inner'
        )
        
        if len(merged) == 0:
            return {'rmse': 0, 'mae': 0, 'mape': 0}
        
        # Calculate metrics
        actual = merged['y'].values
        predicted = merged['yhat'].values
        
        # RMSE
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # MAE
        mae = np.mean(np.abs(actual - predicted))
        
        # MAPE (avoid division by zero)
        mape = np.mean(np.abs((actual - predicted) / np.where(actual != 0, actual, 1))) * 100
        
        return {
            'rmse': round(rmse, 2),
            'mae': round(mae, 2),
            'mape': round(mape, 2)
        }
    
    def save_forecast_to_db(self, forecast: pd.DataFrame, metric_name: str,
                           model_used: str = 'Prophet') -> None:
        """
        Save forecast results to database.
        
        Args:
            forecast: Forecast DataFrame from Prophet
            metric_name: Name of the metric
            model_used: Model name used for forecasting
        """
        conn = get_db_connection()
        
        # Prepare data for database
        forecast_db = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        forecast_db.columns = ['date', 'forecast_value', 'lower_bound', 'upper_bound']
        forecast_db['metric_name'] = metric_name
        forecast_db['model_used'] = model_used
        
        # Only save future predictions
        last_historical_date = pd.Timestamp.now().normalize()
        forecast_db = forecast_db[forecast_db['date'] > last_historical_date]
        
        # Save to database
        forecast_db.to_sql('forecasts', conn, if_exists='append', index=False)
        
        conn.close()
    
    def forecast_all_key_metrics(self) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
        """
        Forecast all key business metrics.
        
        Returns:
            Dictionary mapping metric names to (forecast, accuracy_metrics)
        """
        print("Generating forecasts for key metrics...")
        
        results = {}
        
        # Define metrics to forecast
        metrics_config = [
            ('finance', 'date', 'revenue', 'Revenue'),
            ('finance', 'date', 'expenses', 'Expenses'),
            ('finance', 'date', 'profit', 'Profit'),
            ('hr', 'date', 'turnover_rate_pct', 'Employee Turnover Rate'),
            ('hr', 'date', 'employee_count', 'Employee Count'),
        ]
        
        for table, date_col, value_col, metric_name in metrics_config:
            try:
                print(f"  Forecasting {metric_name}...")
                forecast, metrics = self.forecast_metric(
                    table, date_col, value_col, metric_name
                )
                results[metric_name] = (forecast, metrics)
                
                # Save to database
                self.save_forecast_to_db(forecast, metric_name)
                
                print(f"    ✓ RMSE: {metrics['rmse']:.2f}, MAPE: {metrics['mape']:.2f}%")
                
            except Exception as e:
                print(f"    ✗ Error forecasting {metric_name}: {e}")
        
        return results
    
    def get_forecast_summary(self, metric_name: str) -> pd.DataFrame:
        """
        Get a summary of forecast for a specific metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            DataFrame with forecast summary
        """
        if metric_name not in self.forecasts:
            raise ValueError(f"No forecast found for {metric_name}")
        
        forecast = self.forecasts[metric_name]
        
        # Get future predictions only
        last_date = forecast['ds'].max() - pd.DateOffset(
            months=self.forecast_config['forecast_periods']
        )
        future_forecast = forecast[forecast['ds'] > last_date]
        
        summary = future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        summary.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound']
        
        return summary


def main():
    """Main execution for forecasting"""
    forecaster = TimeSeriesForecaster()
    results = forecaster.forecast_all_key_metrics()
    
    print(f"\n{'='*60}")
    print(f"Forecasting Complete!")
    print(f"Generated {len(results)} forecasts")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
