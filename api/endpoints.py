"""
FastAPI endpoints for OpsIntel360
Provides REST API for data refresh and status checking
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from etl.etl_pipeline import OpsIntelETL
from models.forecasting import TimeSeriesForecaster
from models.anomalies import AnomalyDetector
from models.insights import InsightEngine
from etl.utils import execute_query
import config

# Initialize FastAPI app
app = FastAPI(
    title="OpsIntel360 API",
    description="REST API for OpsIntel360 Business Analytics Platform",
    version="1.0.0"
)

# Global status tracker
refresh_status = {
    "last_refresh": None,
    "status": "idle",
    "message": ""
}


class RefreshRequest(BaseModel):
    """Request model for data refresh"""
    regenerate_data: bool = False
    run_forecasting: bool = True
    run_anomaly_detection: bool = True
    run_insights: bool = True


class StatusResponse(BaseModel):
    """Response model for status endpoint"""
    status: str
    last_refresh: Optional[str]
    message: str
    database_records: Dict[str, int]


def refresh_data_task(request: RefreshRequest):
    """Background task for data refresh"""
    global refresh_status
    
    try:
        refresh_status["status"] = "running"
        refresh_status["message"] = "Starting data refresh..."
        
        # Run ETL pipeline
        refresh_status["message"] = "Running ETL pipeline..."
        etl = OpsIntelETL()
        etl.run_full_pipeline(regenerate_data=request.regenerate_data)
        
        # Run forecasting
        if request.run_forecasting:
            refresh_status["message"] = "Generating forecasts..."
            forecaster = TimeSeriesForecaster()
            forecaster.forecast_all_key_metrics()
        
        # Run anomaly detection
        if request.run_anomaly_detection:
            refresh_status["message"] = "Detecting anomalies..."
            detector = AnomalyDetector()
            detector.detect_all_anomalies()
        
        # Generate insights
        if request.run_insights:
            refresh_status["message"] = "Generating insights..."
            engine = InsightEngine()
            engine.generate_all_insights()
        
        refresh_status["status"] = "completed"
        refresh_status["last_refresh"] = datetime.now().isoformat()
        refresh_status["message"] = "Data refresh completed successfully"
        
    except Exception as e:
        refresh_status["status"] = "failed"
        refresh_status["message"] = f"Error during refresh: {str(e)}"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpsIntel360 API",
        "version": "1.0.0",
        "endpoints": {
            "status": "/status",
            "refresh": "/refresh (POST)",
            "metrics": "/metrics",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        result = execute_query("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status"""
    try:
        # Get record counts from database
        tables = ['finance', 'sales', 'operations', 'hr', 'it_tickets']
        record_counts = {}
        
        for table in tables:
            result = execute_query(f"SELECT COUNT(*) as count FROM {table}")
            record_counts[table] = result['count'].iloc[0] if not result.empty else 0
        
        return StatusResponse(
            status=refresh_status["status"],
            last_refresh=refresh_status["last_refresh"],
            message=refresh_status["message"],
            database_records=record_counts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh")
async def refresh_data(
    request: RefreshRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger data refresh in background
    
    Args:
        request: RefreshRequest with options
        background_tasks: FastAPI background tasks
    
    Returns:
        Status message
    """
    if refresh_status["status"] == "running":
        return JSONResponse(
            status_code=409,
            content={
                "status": "error",
                "message": "Refresh already in progress"
            }
        )
    
    # Start refresh task in background
    background_tasks.add_task(refresh_data_task, request)
    
    return {
        "status": "accepted",
        "message": "Data refresh started in background",
        "check_status_at": "/status"
    }


@app.get("/metrics")
async def get_metrics():
    """Get latest metrics summary"""
    try:
        # Get latest financial metrics
        finance_query = """
            SELECT date, revenue, profit, profit_margin_pct
            FROM finance
            ORDER BY date DESC
            LIMIT 1
        """
        finance = execute_query(finance_query)
        
        # Get latest operations metrics
        ops_query = """
            SELECT date, ontime_delivery_pct, avg_processing_time_hours
            FROM operations
            ORDER BY date DESC
            LIMIT 1
        """
        operations = execute_query(ops_query)
        
        # Get latest HR metrics
        hr_query = """
            SELECT date, employee_count, turnover_rate_pct
            FROM hr
            ORDER BY date DESC
            LIMIT 1
        """
        hr = execute_query(hr_query)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "finance": finance.to_dict('records')[0] if not finance.empty else {},
            "operations": operations.to_dict('records')[0] if not operations.empty else {},
            "hr": hr.to_dict('records')[0] if not hr.empty else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insights/latest")
async def get_latest_insights(limit: int = 10):
    """Get latest generated insights"""
    try:
        query = f"""
            SELECT date, category, insight_text, severity, metric_value
            FROM insights
            ORDER BY created_at DESC
            LIMIT {limit}
        """
        insights = execute_query(query)
        
        return {
            "count": len(insights),
            "insights": insights.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomalies/recent")
async def get_recent_anomalies(days: int = 30):
    """Get recent anomalies"""
    try:
        query = f"""
            SELECT date, metric_name, metric_value, 
                   expected_value, anomaly_score, detection_method
            FROM anomalies
            WHERE date >= date('now', '-{days} days')
            ORDER BY date DESC, anomaly_score DESC
        """
        anomalies = execute_query(query)
        
        return {
            "count": len(anomalies),
            "period_days": days,
            "anomalies": anomalies.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.API_CONFIG["host"],
        port=config.API_CONFIG["port"],
        reload=config.API_CONFIG["reload"]
    )
