# InsightFlow AI

An AI-powered Business Intelligence platform that transforms raw business data into interactive dashboards, machine learning insights, forecasts, and natural language business recommendations using FastAPI, React, PostgreSQL, and Google Gemini.

---

## Live Demo

### Frontend

https://insight-flow-ai-indol.vercel.app

### Backend API

https://insightflow-ai-ttuh.onrender.com

### API Documentation

https://insightflow-ai-ttuh.onrender.com/docs

---

# Key Highlights

- Full-Stack Business Intelligence Platform
- AI Business Copilot powered by Google Gemini
- Interactive Dashboards
- Machine Learning Insights
- Revenue Forecasting
- Retrieval-Augmented AI Responses
- Secure Authentication
- Responsive User Interface
- Cloud Deployment with Vercel & Render

---

# Features

## Authentication

- User Registration
- Secure Login
- JWT Authentication

## Data Management

- Upload CSV datasets
- Upload Excel datasets
- Automatic Data Cleaning
- Dataset Management

## Business Dashboard

- KPI Cards
- Revenue Analysis
- Profit Analysis
- Sales Trends
- Product Performance
- Regional Performance
- Customer Insights

## Interactive Visualizations

- Line Charts
- Bar Charts
- Pie Charts
- Treemap
- Heatmap
- Funnel Chart
- Sankey Diagram
- Geographic Maps

## Machine Learning

- Customer Segmentation
- Anomaly Detection
- Revenue Forecasting

## AI Business Copilot

- Natural Language Business Queries
- AI Business Recommendations
- Context-Aware Dataset Analysis
- Retrieval-Augmented Responses
- Powered by Google Gemini API

## Reports

- Download Business Reports

---

# Technology Stack

## Frontend

- React
- Vite
- Tailwind CSS
- Plotly
- React Simple Maps

## Backend

- FastAPI
- Python
- SQLAlchemy
- Pandas
- PostgreSQL

## Artificial Intelligence

- Google Gemini API
- Retrieval-Augmented Generation (RAG)
- TF-IDF Retrieval

## Development Tools

- Git
- GitHub
- VS Code

---

# Architecture

```
User
   │
   ▼
React Frontend
   │
   ▼
FastAPI Backend
   │
   ├── Authentication
   ├── Analytics Engine
   ├── Machine Learning
   ├── AI Copilot
   │
   ▼
PostgreSQL Database
```

---

# Project Structure

```text
InsightFlow_AI
│
├── backend
│   ├── app
│   ├── uploads
│   ├── vector_store
│   ├── requirements.txt
│   └── .env.example
│
├── frontend
│   ├── src
│   ├── public
│   └── package.json
│
├── screenshots
├── README.md
├── LICENSE
└── .gitignore
```

---

# Prerequisites

Install the following software before running the project.

- Python 3.11 or later
- Node.js
- PostgreSQL
- Git
- Google AI Studio API Key

---

# Installation

Clone the repository.

```bash
git clone https://github.com/maheshdamam/InsightFlow_AI.git
```

Move into the project.

```bash
cd InsightFlow_AI
```

---

# Backend Setup

Move to the backend folder.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a file named `.env` inside the `backend` folder.

```env
GEMINI_API_KEY=your_api_key_here
AI_PROVIDER=gemini
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ENV=development
```

---

Start the backend server.

```bash
uvicorn app.main:app --reload
```

Backend API

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open another terminal.

Move into the frontend folder.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Run the development server.

```bash
npm run dev
```

Open

```
http://localhost:5173
```

---

# Using InsightFlow AI

1. Register a new account.
2. Log in.
3. Upload a CSV or Excel dataset.
4. Explore interactive dashboards.
5. Analyze machine learning insights.
6. Ask business questions using the AI Copilot.
7. Download reports.

---

# Application Preview

## Login

![Login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard-overview.png)

## Analytics

![Analytics](screenshots/dashboard-charts.png)

## Machine Learning

![Machine Learning](screenshots/ml-insights.png)

## AI Copilot

![AI Copilot](screenshots/ai-copilot.png)

## Reports

![Reports](screenshots/download-reports.png)

---

# Roadmap

Future improvements include:

- Role-Based Access Control
- Real-Time Analytics
- Dashboard Customization
- PDF Report Generation
- PowerPoint Export
- Advanced Forecasting Models
- Multi-Database Support
- Multi-Model AI Support
- Conversation History
- Streaming AI Responses

---

# Contributing

Contributions are welcome.

Feel free to fork the repository, open issues, or submit pull requests to improve InsightFlow AI.

---

# License

This project is licensed under the MIT License.

---

# Author

**Mahesh Damam**

GitHub

https://github.com/maheshdamam