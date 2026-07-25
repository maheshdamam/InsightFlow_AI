# InsightFlow AI

InsightFlow AI is a full-stack business intelligence platform that combines interactive dashboards with AI-powered analytics. Users can upload CSV or Excel datasets, explore business performance through visualizations, generate machine learning insights, and interact with a local AI assistant powered by Ollama.

The platform is designed to simplify business analysis by bringing data processing, visualization, forecasting, reporting, and natural language querying into a single application.

---

## Features

### Authentication
- User Registration
- Secure Login

### Data Management
- Upload CSV & Excel files
- Automatic data cleaning
- Dataset management

### Analytics Dashboard
- KPI Cards
- Revenue Analysis
- Profit Analysis
- Category Performance
- Regional Performance
- Customer Insights

### Visualizations
- Line Charts
- Bar Charts
- Pie Charts
- Treemap
- Heatmap
- Sankey Diagram
- Funnel Chart

### Machine Learning
- Customer Segmentation
- Anomaly Detection
- Revenue Forecasting

### AI Copilot
- Natural Language Queries
- Business Insights
- Business Recommendations
- Local LLM powered by Ollama

### Reports
- Download Business Reports

---

## Technology Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Plotly
- React Simple Maps

### Backend
- FastAPI
- Python
- SQLAlchemy
- Pandas
- PostgreSQL

### AI
- Ollama
- Llama 3.1

### Development Tools
- Git
- GitHub
- VS Code

---

## Project Structure

```text
InsightFlow_AI/
│
├── backend/
├── frontend/
├── datasets/
├── reports/
├── screenshots/
└── README.md
```

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/maheshdamam/InsightFlow_AI.git
cd InsightFlow_AI
```

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Application Preview

### Login

![Login](screenshots/login.png)

### Dashboard Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

### Analytics Dashboard

![Analytics Dashboard](screenshots/dashboard-charts.png)

### Machine Learning Insights

![Machine Learning Insights](screenshots/ml-insights.png)

### AI Copilot

![AI Copilot](screenshots/ai-copilot.png)

### Reports

![Reports](screenshots/download-reports.png)

---

## Future Improvements

- Role-based access control
- Real-time analytics
- Cloud deployment
- Advanced forecasting models
- RAG-based document intelligence
- Multiple database integrations

---

## Author

**Mahesh Damam**

GitHub: https://github.com/maheshdamam