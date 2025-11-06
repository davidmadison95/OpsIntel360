# 🚀 OpsIntel360 Quick Start Guide

Get OpsIntel360 up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11 or higher
- ✅ pip package manager
- ✅ 500MB free disk space
- ✅ Internet connection (for dependencies)

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:** Installation of ~20 packages including Streamlit, Prophet, Plotly, etc.

### Step 2: Initialize Data & Database

```bash
# Generate synthetic data
python generate_data.py

# Run ETL pipeline
python etl/etl_pipeline.py
```

**Expected output:** 
- 5 CSV files created in `data/` directory
- SQLite database created at `database/opsintel.db`
- 264 total records loaded

### Step 3: Launch Dashboard

```bash
streamlit run app/dashboard_app.py
```

**Expected output:** Browser opens to `http://localhost:8501` showing the dashboard

## One-Command Setup (Linux/Mac)

Use the automated run script:

```bash
chmod +x run.sh
./run.sh
```

This script will:
1. ✅ Create virtual environment
2. ✅ Install dependencies
3. ✅ Generate data
4. ✅ Run ETL pipeline
5. ✅ Launch dashboard

## Verify Installation

Once the dashboard loads, you should see:
- **KPI Overview Tab**: 8 metrics cards with financial and operational data
- **Forecasting Tab**: Interactive time-series predictions
- **Anomalies Tab**: Outlier detection results
- **Recommendations Tab**: AI-generated insights

## Docker Quick Start

If you prefer Docker:

```bash
docker-compose up --build
```

Access at: `http://localhost:8501`

## Troubleshooting

### Issue: "No module named 'prophet'"
**Solution:** Install Prophet dependencies
```bash
pip install prophet --break-system-packages
```

### Issue: "Database not found"
**Solution:** Run the ETL pipeline
```bash
python etl/etl_pipeline.py
```

### Issue: "Port 8501 already in use"
**Solution:** Stop other Streamlit instances or use different port
```bash
streamlit run app/dashboard_app.py --server.port 8502
```

## Next Steps

1. **Explore the Dashboard**: Navigate through all 4 tabs
2. **Customize Data**: Modify `config.py` to adjust parameters
3. **Add Features**: Extend the platform with your own insights
4. **Deploy**: Use the Dockerfile to deploy to cloud platforms

## Project Structure Overview

```
opsintel360/
├── app/dashboard_app.py    ← Main dashboard (run this)
├── generate_data.py         ← Creates synthetic data
├── etl/etl_pipeline.py      ← Loads data to database
├── models/                  ← Forecasting, anomalies, insights
├── config.py                ← Configuration settings
└── requirements.txt         ← Python dependencies
```

## Default Configuration

- **Data Period**: 24 months (2023-01 to 2024-12)
- **Forecast Horizon**: 6 months
- **Anomaly Threshold**: Z-score > 3
- **Database**: SQLite (no external DB required)

## Sample Outputs

After setup, you'll have:
- **264 records** across 5 business domains
- **5 forecasts** for key metrics
- **~10-20 anomalies** detected (varies)
- **15-25 insights** generated

## Getting Help

- 📖 Full documentation: See `README.md`
- 🐛 Report issues: GitHub Issues
- 💬 Questions: Open a discussion

## Success Indicators

✅ **Setup Successful If:**
- Dashboard loads without errors
- KPI cards show numeric values
- Charts display data
- No red error messages

❌ **Setup Issues If:**
- "Module not found" errors
- Empty charts
- Database errors
- Connection refused

## Performance Notes

- **Initial Load**: 5-10 seconds
- **Forecast Generation**: 10-15 seconds per metric
- **Anomaly Detection**: 5-10 seconds
- **Dashboard Refresh**: Instant

## Data Refresh

To regenerate data and refresh all analytics:

```bash
python etl/etl_pipeline.py --regenerate
python models/forecasting.py
python models/anomalies.py
python models/insights.py
streamlit run app/dashboard_app.py
```

## Congratulations! 🎉

You now have a fully functional business analytics platform!

**What's Next?**
- Customize the synthetic data patterns
- Add your own business logic
- Deploy to Streamlit Cloud
- Share on your portfolio

---

**Need more help?** Check the full README.md or open an issue on GitHub.
