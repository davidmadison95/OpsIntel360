"""
ETL Pipeline for OpsIntel360 Platform
Orchestrates data loading from CSV files to SQLite database
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
import config
from etl.utils import (
    init_database, load_csv_to_db, get_db_connection,
    get_summary_statistics, clean_dataframe
)


class OpsIntelETL:
    """Main ETL pipeline class for OpsIntel360 platform"""
    
    def __init__(self):
        """Initialize ETL pipeline"""
        self.data_dir = config.DATA_DIR
        self.database_path = config.DATABASE_PATH
        self.tables = ['finance', 'sales', 'operations', 'hr', 'it_tickets']
        
    def run_full_pipeline(self, regenerate_data: bool = False) -> None:
        """
        Run the complete ETL pipeline.
        
        Args:
            regenerate_data: Whether to regenerate synthetic data
        """
        print("="*60)
        print("OpsIntel360 ETL Pipeline Starting...")
        print("="*60)
        
        # Step 1: Initialize database
        print("\n[1/5] Initializing database...")
        self._init_db()
        
        # Step 2: Generate or validate data
        print("\n[2/5] Checking data files...")
        if regenerate_data or not self._data_files_exist():
            print("  Generating new synthetic data...")
            self._generate_data()
        else:
            print("  ✓ Data files found")
        
        # Step 3: Load data into database
        print("\n[3/5] Loading data into database...")
        self._load_all_data()
        
        # Step 4: Data quality checks
        print("\n[4/5] Running data quality checks...")
        self._run_quality_checks()
        
        # Step 5: Generate summary report
        print("\n[5/5] Generating summary report...")
        self._generate_summary()
        
        print("\n" + "="*60)
        print("ETL Pipeline Completed Successfully!")
        print("="*60)
        
    def _init_db(self) -> None:
        """Initialize database with schema"""
        try:
            init_database()
        except Exception as e:
            print(f"  ✗ Error initializing database: {e}")
            raise
    
    def _data_files_exist(self) -> bool:
        """Check if all required CSV files exist"""
        required_files = [
            'finance.csv', 'sales.csv', 'operations.csv', 
            'hr.csv', 'it_tickets.csv'
        ]
        return all((self.data_dir / f).exists() for f in required_files)
    
    def _generate_data(self) -> None:
        """Generate synthetic data"""
        try:
            from generate_data import generate_all_data
            generate_all_data()
        except Exception as e:
            print(f"  ✗ Error generating data: {e}")
            raise
    
    def _load_all_data(self) -> None:
        """Load all CSV files into database"""
        load_results = {}
        
        for table in self.tables:
            csv_path = self.data_dir / f"{table}.csv"
            
            try:
                rows_loaded = load_csv_to_db(csv_path, table, if_exists='replace')
                load_results[table] = rows_loaded
                print(f"  ✓ {table}: {rows_loaded} rows loaded")
            except Exception as e:
                print(f"  ✗ {table}: Error loading data - {e}")
                load_results[table] = 0
        
        self.load_results = load_results
    
    def _run_quality_checks(self) -> None:
        """Run data quality checks"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        checks_passed = 0
        checks_failed = 0
        
        for table in self.tables:
            try:
                # Check 1: Row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"  ✓ {table}: {count} rows")
                    checks_passed += 1
                else:
                    print(f"  ✗ {table}: No data found")
                    checks_failed += 1
                
                # Check 2: Date range
                cursor.execute(f"""
                    SELECT MIN(date), MAX(date) FROM {table}
                """)
                min_date, max_date = cursor.fetchone()
                print(f"    Date range: {min_date} to {max_date}")
                
                # Check 3: Null values in key columns
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table} WHERE date IS NULL
                """)
                null_dates = cursor.fetchone()[0]
                
                if null_dates > 0:
                    print(f"    ⚠ Warning: {null_dates} rows with null dates")
                
            except Exception as e:
                print(f"  ✗ {table}: Quality check failed - {e}")
                checks_failed += 1
        
        conn.close()
        
        print(f"\n  Summary: {checks_passed} checks passed, {checks_failed} checks failed")
    
    def _generate_summary(self) -> None:
        """Generate and display summary statistics"""
        conn = get_db_connection()
        
        # Overall statistics
        print("\n  Database Summary:")
        print("  " + "-"*50)
        
        for table in self.tables:
            try:
                # Get row count
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Get date range
                cursor.execute(f"""
                    SELECT MIN(date), MAX(date) FROM {table}
                """)
                min_date, max_date = cursor.fetchone()
                
                # Get column count
                cursor.execute(f"PRAGMA table_info({table})")
                columns = len(cursor.fetchall())
                
                print(f"  {table.upper()}")
                print(f"    Records: {count:,}")
                print(f"    Columns: {columns}")
                print(f"    Period: {min_date} to {max_date}")
                print()
                
            except Exception as e:
                print(f"  Error getting summary for {table}: {e}")
        
        conn.close()
        
        # Save summary report
        summary_report = {
            'pipeline_run_date': datetime.now().isoformat(),
            'tables_loaded': len(self.tables),
            'total_rows': sum(self.load_results.values()) if hasattr(self, 'load_results') else 0,
            'database_path': str(self.database_path)
        }
        
        import json
        report_path = config.BASE_DIR / 'etl_summary.json'
        with open(report_path, 'w') as f:
            json.dump(summary_report, f, indent=2)
        
        print(f"  Summary report saved to: {report_path}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='OpsIntel360 ETL Pipeline'
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate synthetic data'
    )
    
    args = parser.parse_args()
    
    # Run ETL pipeline
    etl = OpsIntelETL()
    etl.run_full_pipeline(regenerate_data=args.regenerate)


if __name__ == "__main__":
    main()
