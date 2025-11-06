# 📊 OpsIntel360 - Business Operations Insights Dashboard

> A comprehensive, production-ready data analytics and forecasting platform providing actionable insights across Finance, Sales, Operations, HR, and IT departments.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red)
![Prophet](https://img.shields.io/badge/Prophet-1.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Project Overview

OpsIntel360 is a full-stack data analytics platform that combines:
- **Time-series forecasting** using Facebook Prophet
- **Anomaly detection** with Isolation Forest and Z-Score methods
- **Interactive visualizations** with Plotly
- **AI-generated insights** and recommendations
- **Real-time dashboards** built with Streamlit

Perfect for showcasing data analytics and machine learning engineering capabilities in a portfolio.

## ✨ Key Features

### 📈 Multi-Domain Analytics
- **Finance**: Revenue, expenses, profit margins, budget variance
- **Sales**: Regional performance, conversion rates, deal sizes
- **Operations**: Order processing, on-time delivery, efficiency metrics
- **HR**: Employee count, turnover rates, satisfaction scores
- **IT Support**: Ticket volumes, resolution times, priority analysis

### 🔮 Advanced Forecasting
- Facebook Prophet time-series forecasting
- Configurable forecast horizons (3-12 months)
- Confidence intervals and accuracy metrics (RMSE, MAE, MAPE)
- Interactive forecast visualization

### ⚠️ Intelligent Anomaly Detection
- Dual detection methods: Z-Score and Isolation Forest
- Automatic outlier identification
- Contextual anomaly explanations
- Historical comparison visualizations

### 💡 AI-Powered Insights
- Rule-based recommendation engine
- Severity classification (Critical, Warning, Info)
- Category-specific insights
- Exportable reports (JSON)

### 🎨 Modern Dashboard
- Clean, professional UI with custom CSS
- Interactive Plotly charts
- Real-time KPI cards
- Multi-tab navigation
- Responsive design

## 🏗️ Project Structure

```
opsintel360/
├── data/                          # Generated CSV datasets
│   ├── finance.csv
│   ├── sales.csv
│   ├── operations.csv
│   ├── hr.csv
│   └── it_tickets.csv
├── database/                      # SQLite database
│   ├── schema.sql
│   └── opsintel.db
├── etl/                          # ETL pipeline
│   ├── etl_pipeline.py           # Main ETL orchestration
│   └── utils.py                  # Database utilities
├── models/                       # ML models
│   ├── forecasting.py            # Prophet forecasting
│   ├── anomalies.py              # Anomaly detection
│   └── insights.py               # Insight generation
├── app/                          # Streamlit application
│   └── dashboard_app.py          # Main dashboard
├── config.py                     # Configuration settings
├── generate_data.py              # Synthetic data generation
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Service orchestration
└── README.md                     # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or conda
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/opsintel360.git
cd opsintel360
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate synthetic data and initialize database**
```bash
python generate_data.py
python etl/etl_pipeline.py
```

5. **Run the dashboard**
```bash
streamlit run app/dashboard_app.py
```

6. **Open browser** to `http://localhost:8501`

#### Option 2: Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access dashboard** at `http://localhost:8501`

## 📊 Usage Guide

### Running the ETL Pipeline

The ETL pipeline loads data from CSV files into SQLite:

```bash
# Run with default settings
python etl/etl_pipeline.py

# Regenerate data before loading
python etl/etl_pipeline.py --regenerate
```

### Generating Forecasts

Run forecasting separately for all key metrics:

```bash
python models/forecasting.py
```

### Detecting Anomalies

Execute anomaly detection across all metrics:

```bash
python models/anomalies.py
```

### Generating Insights

Generate AI-powered business recommendations:

```bash
python models/insights.py
```

## 🎨 Dashboard Features

### KPI Overview Tab
- **Real-time metrics**: Revenue, Profit, Margins, Delivery Performance
- **Trend visualizations**: Financial performance over time
- **Regional analysis**: Sales breakdown by geography
- **MoM comparisons**: Month-over-month growth indicators

### Forecasting Tab
- **Interactive predictions**: Select metrics and forecast horizons
- **Model accuracy**: RMSE, MAE, and MAPE metrics
- **Confidence intervals**: Upper and lower bound visualizations
- **Forecast tables**: Detailed numerical predictions

### Anomalies Tab
- **Automated detection**: Identifies unusual patterns
- **Visual highlighting**: Anomalies marked on time-series charts
- **Detailed analysis**: Z-scores and anomaly scores
- **Contextual insights**: Explanations for detected outliers

### Recommendations Tab
- **Severity filtering**: Critical, Warning, Info classifications
- **Category filtering**: Finance, Sales, Operations, HR, IT
- **Actionable insights**: Specific, data-driven recommendations
- **Export functionality**: Download insights as JSON

## 🔧 Configuration

### Database Settings
Edit `config.py` to customize:
- Data generation parameters (start date, periods, frequency)
- Forecast configuration (horizon, seasonality, priors)
- Anomaly detection thresholds
- KPI targets and thresholds

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

## 📈 Data Generation

The platform includes a sophisticated synthetic data generator:

```python
from generate_data import generate_all_data

# Generate 24 months of synthetic business data
finance_df, sales_df, operations_df, hr_df, it_tickets_df = generate_all_data()
```

**Data Characteristics:**
- Realistic trends and seasonality
- Region-specific patterns
- Correlated metrics (e.g., revenue drives expenses)
- Time-series improvements (e.g., efficiency gains)
- Random noise for authenticity

## 🧪 Testing

### Run Manual Tests
```bash
# Test data generation
python generate_data.py

# Test ETL pipeline
python etl/etl_pipeline.py

# Test forecasting
python models/forecasting.py

# Test anomaly detection
python models/anomalies.py

# Test insights generation
python models/insights.py
```

## 📦 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect repository
4. Deploy with `app/dashboard_app.py` as entry point

### Deploy to Heroku

1. Create `Procfile`:
```
web: streamlit run app/dashboard_app.py --server.port=$PORT
```

2. Deploy:
```bash
heroku create opsintel360
git push heroku main
```

### Deploy with Docker

```bash
# Build image
docker build -t opsintel360 .

# Run container
docker run -p 8501:8501 opsintel360
```

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.11 |
| **Data Processing** | Pandas, NumPy, SQLAlchemy |
| **Machine Learning** | Prophet, Scikit-learn |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Web Framework** | Streamlit |
| **Database** | SQLite |
| **Deployment** | Docker, Docker Compose |

## 📚 Key Dependencies

- **Prophet 1.1**: Time-series forecasting
- **Streamlit 1.30**: Interactive web applications
- **Plotly 5.18**: Interactive visualizations
- **Scikit-learn 1.4**: Anomaly detection (Isolation Forest)
- **Pandas 2.1**: Data manipulation
- **SQLAlchemy 2.0**: Database ORM

## 🎓 Learning Outcomes

This project demonstrates proficiency in:
- ✅ Full-stack data engineering
- ✅ Time-series forecasting with Prophet
- ✅ Anomaly detection algorithms
- ✅ ETL pipeline design
- ✅ Database schema design
- ✅ Interactive dashboard development
- ✅ Python best practices and code organization
- ✅ Docker containerization
- ✅ Data visualization techniques
- ✅ Business intelligence and KPI tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**David Madison**
- Graduate Student in Data Analytics
- Research Assistant in AI & Robotics
- [LinkedIn](https://www.linkedin.com/in/davidmadison95/) | [GitHub](https://github.com/davidmadison95)

## 🙏 Acknowledgments

- Built with Python, Streamlit, Prophet, and other open-source technologies.

## 📧 Contact

For questions or feedback, please open an issue or contact:
- Email: davidmadison95@yahoo.com
- LinkedIn: [https://www.linkedin.com/in/davidmadison95/]

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

Built with ❤️ using Python, Streamlit, and Prophet
