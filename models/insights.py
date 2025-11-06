"""
Insight generation engine for OpsIntel360
Auto-generates business recommendations based on data patterns
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import json

import config
from etl.utils import execute_query, insert_insight, calculate_percentage_change


class InsightEngine:
    """
    Generate actionable business insights from data patterns
    """
    
    def __init__(self):
        """Initialize insight engine"""
        self.thresholds = config.KPI_THRESHOLDS
        self.insights: List[Dict] = []
        
    def analyze_revenue_trends(self) -> List[Dict]:
        """
        Analyze revenue trends and generate insights.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Get recent revenue data
        query = """
            SELECT date, revenue, profit_margin_pct
            FROM finance
            ORDER BY date DESC
            LIMIT 6
        """
        df = execute_query(query)
        
        if len(df) < 2:
            return insights
        
        df = df.sort_values('date')
        
        # Calculate MoM growth
        latest_revenue = df['revenue'].iloc[-1]
        prev_revenue = df['revenue'].iloc[-2]
        growth_rate = ((latest_revenue - prev_revenue) / prev_revenue * 100)
        
        # Generate insight based on growth
        if growth_rate > self.thresholds['revenue_growth']['good']:
            severity = 'info'
            insight_text = (
                f"💰 Revenue growth accelerated by {growth_rate:.1f}% MoM. "
                f"Consider scaling successful marketing channels and expanding sales team."
            )
        elif growth_rate < self.thresholds['revenue_growth']['critical']:
            severity = 'critical'
            insight_text = (
                f"⚠️ Revenue declined by {abs(growth_rate):.1f}% MoM. "
                f"Immediate action needed: Review pricing strategy, competitor analysis, "
                f"and customer retention programs."
            )
        elif growth_rate < self.thresholds['revenue_growth']['warning']:
            severity = 'warning'
            insight_text = (
                f"📊 Revenue growth slowed to {growth_rate:.1f}% MoM. "
                f"Monitor closely and consider promotional campaigns or new customer acquisition strategies."
            )
        else:
            severity = 'info'
            insight_text = (
                f"📈 Revenue growing steadily at {growth_rate:.1f}% MoM. "
                f"Maintain current strategies while exploring new market opportunities."
            )
        
        insights.append({
            'date': str(df['date'].iloc[-1]),
            'category': 'finance',
            'insight_text': insight_text,
            'severity': severity,
            'metric_value': growth_rate
        })
        
        # Analyze profit margin
        latest_margin = df['profit_margin_pct'].iloc[-1]
        
        if latest_margin < self.thresholds['profit_margin']['critical']:
            insights.append({
                'date': str(df['date'].iloc[-1]),
                'category': 'finance',
                'insight_text': (
                    f"🔴 Profit margin critically low at {latest_margin:.1f}%. "
                    f"Urgent review of cost structure and pricing needed."
                ),
                'severity': 'critical',
                'metric_value': latest_margin
            })
        elif latest_margin > self.thresholds['profit_margin']['good']:
            insights.append({
                'date': str(df['date'].iloc[-1]),
                'category': 'finance',
                'insight_text': (
                    f"✅ Strong profit margin at {latest_margin:.1f}%. "
                    f"Opportunity to reinvest in growth initiatives."
                ),
                'severity': 'info',
                'metric_value': latest_margin
            })
        
        return insights
    
    def analyze_sales_performance(self) -> List[Dict]:
        """
        Analyze sales performance by region.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Get recent sales data by region
        query = """
            SELECT date, region, 
                   SUM(units_sold) as total_units,
                   AVG(conversion_rate_pct) as avg_conversion
            FROM sales
            WHERE date >= date('now', '-3 months')
            GROUP BY date, region
            ORDER BY date DESC
        """
        df = execute_query(query)
        
        if df.empty:
            return insights
        
        # Get latest month data
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        # Find best and worst performing regions
        best_region = latest_data.loc[latest_data['total_units'].idxmax()]
        worst_region = latest_data.loc[latest_data['total_units'].idxmin()]
        
        insights.append({
            'date': str(latest_date),
            'category': 'sales',
            'insight_text': (
                f"🏆 {best_region['region']} region is outperforming with "
                f"{best_region['total_units']:.0f} units sold. "
                f"Consider replicating successful strategies in other regions."
            ),
            'severity': 'info',
            'metric_value': float(best_region['total_units'])
        })
        
        if worst_region['total_units'] < best_region['total_units'] * 0.7:
            insights.append({
                'date': str(latest_date),
                'category': 'sales',
                'insight_text': (
                    f"⚠️ {worst_region['region']} region underperforming with only "
                    f"{worst_region['total_units']:.0f} units sold. "
                    f"Requires targeted support and sales enablement."
                ),
                'severity': 'warning',
                'metric_value': float(worst_region['total_units'])
            })
        
        return insights
    
    def analyze_operations_efficiency(self) -> List[Dict]:
        """
        Analyze operational efficiency metrics.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        query = """
            SELECT date, ontime_delivery_pct, avg_processing_time_hours, defect_rate_pct
            FROM operations
            ORDER BY date DESC
            LIMIT 6
        """
        df = execute_query(query)
        
        if df.empty:
            return insights
        
        df = df.sort_values('date')
        latest = df.iloc[-1]
        
        # On-time delivery analysis
        ontime = latest['ontime_delivery_pct']
        
        if ontime < self.thresholds['ontime_delivery']['critical']:
            insights.append({
                'date': str(latest['date']),
                'category': 'operations',
                'insight_text': (
                    f"🔴 On-time delivery dropped to {ontime:.1f}%. "
                    f"Critical: Review logistics processes and staffing levels."
                ),
                'severity': 'critical',
                'metric_value': ontime
            })
        elif ontime > self.thresholds['ontime_delivery']['good']:
            insights.append({
                'date': str(latest['date']),
                'category': 'operations',
                'insight_text': (
                    f"✅ Excellent on-time delivery at {ontime:.1f}%. "
                    f"Maintain current operational excellence."
                ),
                'severity': 'info',
                'metric_value': ontime
            })
        
        # Processing time trend
        if len(df) >= 3:
            recent_avg = df['avg_processing_time_hours'].iloc[-3:].mean()
            older_avg = df['avg_processing_time_hours'].iloc[:3].mean()
            improvement = ((older_avg - recent_avg) / older_avg * 100)
            
            if improvement > 10:
                insights.append({
                    'date': str(latest['date']),
                    'category': 'operations',
                    'insight_text': (
                        f"📉 Processing time improved by {improvement:.1f}%. "
                        f"Great progress on operational efficiency!"
                    ),
                    'severity': 'info',
                    'metric_value': improvement
                })
        
        return insights
    
    def analyze_hr_metrics(self) -> List[Dict]:
        """
        Analyze HR and employee-related metrics.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        query = """
            SELECT date, employee_count, turnover_rate_pct, 
                   satisfaction_score, absenteeism_rate_pct
            FROM hr
            ORDER BY date DESC
            LIMIT 6
        """
        df = execute_query(query)
        
        if df.empty:
            return insights
        
        df = df.sort_values('date')
        latest = df.iloc[-1]
        
        # Turnover analysis
        turnover = latest['turnover_rate_pct']
        
        if turnover > self.thresholds['employee_turnover']['critical']:
            insights.append({
                'date': str(latest['date']),
                'category': 'hr',
                'insight_text': (
                    f"🔴 Employee turnover at critical level: {turnover:.1f}%. "
                    f"Immediate action: Review compensation, culture, and exit interviews."
                ),
                'severity': 'critical',
                'metric_value': turnover
            })
        elif turnover < self.thresholds['employee_turnover']['good']:
            insights.append({
                'date': str(latest['date']),
                'category': 'hr',
                'insight_text': (
                    f"✅ Healthy turnover rate at {turnover:.1f}%. "
                    f"Strong employee retention indicates positive culture."
                ),
                'severity': 'info',
                'metric_value': turnover
            })
        
        # Employee growth trend
        if len(df) >= 2:
            growth = latest['employee_count'] - df['employee_count'].iloc[0]
            if growth > 10:
                insights.append({
                    'date': str(latest['date']),
                    'category': 'hr',
                    'insight_text': (
                        f"📈 Team grew by {growth} employees. "
                        f"Ensure onboarding processes can scale with growth."
                    ),
                    'severity': 'info',
                    'metric_value': growth
                })
        
        return insights
    
    def analyze_it_performance(self) -> List[Dict]:
        """
        Analyze IT support performance metrics.
        
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        query = """
            SELECT date, priority,
                   SUM(tickets_opened) as total_opened,
                   SUM(tickets_closed) as total_closed,
                   AVG(avg_resolution_time_hours) as avg_resolution
            FROM it_tickets
            WHERE date >= date('now', '-3 months')
            GROUP BY date, priority
            ORDER BY date DESC
        """
        df = execute_query(query)
        
        if df.empty:
            return insights
        
        # Analyze critical tickets
        critical_df = df[df['priority'] == 'Critical']
        if not critical_df.empty:
            latest_critical = critical_df.iloc[0]
            resolution_time = latest_critical['avg_resolution']
            
            if resolution_time > self.thresholds['ticket_resolution_hours']['critical']:
                insights.append({
                    'date': str(latest_critical['date']),
                    'category': 'it',
                    'insight_text': (
                        f"⚠️ Critical ticket resolution time at {resolution_time:.1f} hours. "
                        f"Consider increasing IT support staffing or implementing automation."
                    ),
                    'severity': 'warning',
                    'metric_value': resolution_time
                })
            elif resolution_time < self.thresholds['ticket_resolution_hours']['good']:
                insights.append({
                    'date': str(latest_critical['date']),
                    'category': 'it',
                    'insight_text': (
                        f"✅ Excellent critical ticket resolution: {resolution_time:.1f} hours. "
                        f"IT team is performing well."
                    ),
                    'severity': 'info',
                    'metric_value': resolution_time
                })
        
        # Ticket backlog analysis
        latest_date = df['date'].max()
        latest_all = df[df['date'] == latest_date]
        total_opened = latest_all['total_opened'].sum()
        total_closed = latest_all['total_closed'].sum()
        
        if total_closed < total_opened * 0.9:
            backlog_rate = ((total_opened - total_closed) / total_opened * 100)
            insights.append({
                'date': str(latest_date),
                'category': 'it',
                'insight_text': (
                    f"📊 Ticket backlog growing ({backlog_rate:.1f}% of opened tickets pending). "
                    f"Review resource allocation and ticket prioritization."
                ),
                'severity': 'warning',
                'metric_value': backlog_rate
            })
        
        return insights
    
    def generate_all_insights(self) -> List[Dict]:
        """
        Generate insights across all business domains.
        
        Returns:
            List of all generated insights
        """
        print("Generating business insights...")
        
        all_insights = []
        
        # Generate insights from each domain
        insight_functions = [
            ('Finance', self.analyze_revenue_trends),
            ('Sales', self.analyze_sales_performance),
            ('Operations', self.analyze_operations_efficiency),
            ('HR', self.analyze_hr_metrics),
            ('IT', self.analyze_it_performance),
        ]
        
        for domain, func in insight_functions:
            try:
                print(f"  Analyzing {domain}...")
                insights = func()
                all_insights.extend(insights)
                print(f"    ✓ Generated {len(insights)} insights")
            except Exception as e:
                print(f"    ✗ Error analyzing {domain}: {e}")
        
        # Save insights to database
        for insight in all_insights:
            try:
                insert_insight(**insight)
            except Exception as e:
                print(f"    Warning: Could not save insight: {e}")
        
        self.insights = all_insights
        
        # Save to JSON file
        self._save_insights_to_json(all_insights)
        
        return all_insights
    
    def _save_insights_to_json(self, insights: List[Dict]) -> None:
        """
        Save insights to JSON file for export.
        
        Args:
            insights: List of insight dictionaries
        """
        output_path = config.BASE_DIR / 'insights.json'
        
        with open(output_path, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_insights': len(insights),
                'insights': insights
            }, f, indent=2)
        
        print(f"\n  Insights saved to: {output_path}")
    
    def get_insights_by_severity(self, severity: str) -> List[Dict]:
        """
        Filter insights by severity level.
        
        Args:
            severity: 'critical', 'warning', or 'info'
            
        Returns:
            Filtered list of insights
        """
        return [i for i in self.insights if i['severity'] == severity]
    
    def get_insights_by_category(self, category: str) -> List[Dict]:
        """
        Filter insights by business category.
        
        Args:
            category: 'finance', 'sales', 'operations', 'hr', or 'it'
            
        Returns:
            Filtered list of insights
        """
        return [i for i in self.insights if i['category'] == category]


def main():
    """Main execution for insight generation"""
    engine = InsightEngine()
    insights = engine.generate_all_insights()
    
    print(f"\n{'='*60}")
    print(f"Generated {len(insights)} total insights")
    
    # Show summary by severity
    critical = len(engine.get_insights_by_severity('critical'))
    warning = len(engine.get_insights_by_severity('warning'))
    info = len(engine.get_insights_by_severity('info'))
    
    print(f"  Critical: {critical}")
    print(f"  Warning: {warning}")
    print(f"  Info: {info}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
