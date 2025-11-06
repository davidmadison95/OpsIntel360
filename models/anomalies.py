"""
Anomaly detection module for OpsIntel360
Uses Isolation Forest and Z-Score methods
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

import config
from etl.utils import execute_query, insert_anomaly


class AnomalyDetector:
    """
    Detect anomalies in business metrics using multiple methods
    """
    
    def __init__(self):
        """Initialize anomaly detector with configuration"""
        self.anomaly_config = config.ANOMALY_CONFIG
        self.anomalies: Dict[str, pd.DataFrame] = {}
        
    def detect_zscore_anomalies(self, df: pd.DataFrame, column: str,
                                threshold: Optional[float] = None) -> pd.DataFrame:
        """
        Detect anomalies using Z-score method.
        
        Args:
            df: Input DataFrame
            column: Column to analyze
            threshold: Z-score threshold (default from config)
            
        Returns:
            DataFrame with anomaly flags and scores
        """
        if threshold is None:
            threshold = self.anomaly_config['z_score_threshold']
        
        df = df.copy()
        
        # Calculate z-scores
        mean = df[column].mean()
        std = df[column].std()
        
        if std == 0:
            df['z_score'] = 0
            df['is_anomaly'] = False
        else:
            df['z_score'] = np.abs((df[column] - mean) / std)
            df['is_anomaly'] = df['z_score'] > threshold
        
        df['expected_value'] = mean
        df['detection_method'] = 'z-score'
        
        return df
    
    def detect_isolation_forest_anomalies(self, df: pd.DataFrame,
                                         columns: List[str],
                                         contamination: Optional[float] = None) -> pd.DataFrame:
        """
        Detect anomalies using Isolation Forest algorithm.
        
        Args:
            df: Input DataFrame
            columns: List of columns to analyze
            contamination: Expected proportion of outliers
            
        Returns:
            DataFrame with anomaly flags and scores
        """
        if contamination is None:
            contamination = self.anomaly_config['contamination']
        
        df = df.copy()
        
        # Prepare data
        X = df[columns].values
        
        # Handle missing values
        if np.isnan(X).any():
            X = np.nan_to_num(X, nan=np.nanmean(X, axis=0))
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = iso_forest.fit_predict(X_scaled)
        anomaly_scores = iso_forest.score_samples(X_scaled)
        
        df['is_anomaly'] = predictions == -1
        df['anomaly_score'] = -anomaly_scores  # Invert so higher = more anomalous
        df['detection_method'] = 'isolation_forest'
        
        return df
    
    def detect_metric_anomalies(self, table_name: str, metric_column: str,
                                date_column: str = 'date',
                                method: str = 'z-score') -> pd.DataFrame:
        """
        Detect anomalies for a specific metric from database.
        
        Args:
            table_name: Database table name
            metric_column: Column containing the metric
            date_column: Date column name
            method: Detection method ('z-score' or 'isolation_forest')
            
        Returns:
            DataFrame with anomaly detection results
        """
        # Get data from database
        query = f"""
            SELECT {date_column}, {metric_column}
            FROM {table_name}
            WHERE {metric_column} IS NOT NULL
            ORDER BY {date_column}
        """
        df = execute_query(query)
        
        if df.empty:
            return pd.DataFrame()
        
        # Detect anomalies based on method
        if method == 'z-score':
            result_df = self.detect_zscore_anomalies(df, metric_column)
        elif method == 'isolation_forest':
            result_df = self.detect_isolation_forest_anomalies(df, [metric_column])
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Filter to only anomalies
        anomalies = result_df[result_df['is_anomaly']].copy()
        anomalies['metric_name'] = metric_column
        anomalies['table_name'] = table_name
        
        return anomalies
    
    def detect_all_anomalies(self) -> Dict[str, pd.DataFrame]:
        """
        Detect anomalies across all key business metrics.
        
        Returns:
            Dictionary mapping metric names to anomaly DataFrames
        """
        print("Detecting anomalies across all metrics...")
        
        results = {}
        
        # Define metrics to analyze
        metrics_config = [
            ('finance', 'revenue', 'Revenue'),
            ('finance', 'expenses', 'Expenses'),
            ('finance', 'profit', 'Profit'),
            ('finance', 'profit_margin_pct', 'Profit Margin'),
            ('operations', 'avg_processing_time_hours', 'Processing Time'),
            ('operations', 'ontime_delivery_pct', 'On-Time Delivery'),
            ('hr', 'turnover_rate_pct', 'Turnover Rate'),
            ('hr', 'absenteeism_rate_pct', 'Absenteeism Rate'),
        ]
        
        for table, metric_col, metric_name in metrics_config:
            try:
                print(f"  Analyzing {metric_name}...")
                anomalies = self.detect_metric_anomalies(
                    table, metric_col, method='z-score'
                )
                
                if not anomalies.empty:
                    results[metric_name] = anomalies
                    print(f"    ✓ Found {len(anomalies)} anomalies")
                    
                    # Save to database
                    self._save_anomalies_to_db(anomalies, metric_name)
                else:
                    print(f"    ✓ No anomalies detected")
                    
            except Exception as e:
                print(f"    ✗ Error analyzing {metric_name}: {e}")
        
        self.anomalies = results
        return results
    
    def _save_anomalies_to_db(self, anomalies: pd.DataFrame, 
                             metric_name: str) -> None:
        """
        Save detected anomalies to database.
        
        Args:
            anomalies: DataFrame with anomaly data
            metric_name: Name of the metric
        """
        for _, row in anomalies.iterrows():
            try:
                insert_anomaly(
                    date=str(row['date']),
                    metric_name=metric_name,
                    metric_value=float(row[anomalies['metric_name'].iloc[0]]),
                    expected_value=float(row.get('expected_value', 0)),
                    anomaly_score=float(row.get('anomaly_score', row.get('z_score', 0))),
                    detection_method=row['detection_method']
                )
            except Exception as e:
                print(f"      Warning: Could not save anomaly: {e}")
    
    def get_anomaly_summary(self) -> pd.DataFrame:
        """
        Get summary of all detected anomalies.
        
        Returns:
            DataFrame with anomaly summary
        """
        if not self.anomalies:
            return pd.DataFrame()
        
        summary_data = []
        
        for metric_name, anomalies_df in self.anomalies.items():
            summary_data.append({
                'Metric': metric_name,
                'Anomalies Count': len(anomalies_df),
                'Latest Anomaly': anomalies_df['date'].max(),
                'Detection Method': anomalies_df['detection_method'].iloc[0]
            })
        
        return pd.DataFrame(summary_data)
    
    def get_recent_anomalies(self, days: int = 90) -> pd.DataFrame:
        """
        Get anomalies from recent time period.
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame with recent anomalies
        """
        query = f"""
            SELECT 
                date,
                metric_name,
                metric_value,
                expected_value,
                anomaly_score,
                detection_method
            FROM anomalies
            WHERE date >= date('now', '-{days} days')
            ORDER BY date DESC, anomaly_score DESC
        """
        
        return execute_query(query)
    
    def generate_anomaly_insights(self, anomalies: pd.DataFrame,
                                  metric_name: str) -> List[str]:
        """
        Generate human-readable insights from anomalies.
        
        Args:
            anomalies: DataFrame with anomaly data
            metric_name: Name of the metric
            
        Returns:
            List of insight strings
        """
        insights = []
        
        if anomalies.empty:
            return insights
        
        # Get metric column name
        metric_col = anomalies['metric_name'].iloc[0]
        
        for _, row in anomalies.head(3).iterrows():  # Top 3 anomalies
            date = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
            value = row[metric_col]
            
            if 'expected_value' in row:
                expected = row['expected_value']
                deviation = ((value - expected) / expected * 100) if expected != 0 else 0
                
                direction = "higher" if value > expected else "lower"
                
                insight = (
                    f"⚠️ {metric_name} on {date} was {abs(deviation):.1f}% {direction} "
                    f"than expected ({value:.2f} vs {expected:.2f})"
                )
            else:
                insight = (
                    f"⚠️ {metric_name} showed unusual value on {date}: {value:.2f}"
                )
            
            insights.append(insight)
        
        return insights


def main():
    """Main execution for anomaly detection"""
    detector = AnomalyDetector()
    results = detector.detect_all_anomalies()
    
    print(f"\n{'='*60}")
    print("Anomaly Detection Complete!")
    print(f"Analyzed {len(results)} metrics")
    
    summary = detector.get_anomaly_summary()
    if not summary.empty:
        print("\nSummary:")
        print(summary.to_string(index=False))
    
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
