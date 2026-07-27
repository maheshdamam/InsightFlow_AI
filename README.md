# InsightFlow AI

InsightFlow AI is a full-stack Business Intelligence platform that combines interactive dashboards with AI-powered analytics. It enables users to upload business datasets, visualize key metrics, discover trends through machine learning, and interact with an AI Copilot using natural language.

The goal of the project is to bring business analytics, visualization, forecasting, and AI-driven insights into a single platform that is easy to use and extend.

---
## Live Demo

Frontend:
https://your-vercel-link.vercel.app

Backend API:
https://your-render-link.onrender.com

Swagger Docs:
https://your-render-link.onrender.com/api/docs

## Features

### Authentication

- User Registration
- Secure Login

### Data Management

- Upload CSV and Excel datasets
- Automatic data cleaning
- Dataset management

### Business Dashboard

- KPI Cards
- Revenue Analysis
- Profit Analysis
- Sales Trends
- Product Performance
- Regional Performance
- Customer Insights

### Data Visualization

- Line Charts
- Bar Charts
- Pie Charts
- Treemap
- Heatmap
- Sankey Diagram
- Funnel Chart
- Interactive Geographic Map

### Machine Learning

- Customer Segmentation
- Anomaly Detection
- Revenue Forecasting

### AI Copilot

- Natural Language Business Queries
- AI-Powered Business Insights
- Actionable Recommendations
- Context-Aware Dataset Analysis
- Powered by Google Gemini 2.5 Flash

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

### Artificial Intelligence

- Google Gemini 2.5 Flash
- Retrieval-Augmented Context (TF-IDF)

### Development Tools

- Git
- GitHub
- VS Code

---

## Project Structure

```text
InsightFlow_AI
│
├── backend
├── frontend
├── datasets
├── reports
├── screenshots
├── LICENSE
├── README.md
└── .gitignore
```

---

## Prerequisites

Before running the project, install the following software:

- Python 3.11 or later
- Node.js
- PostgreSQL
Google AI Studio API Key


---

## Installation

Clone the repository.

```bash
git clone https://github.com/maheshdamam/InsightFlow_AI.git
```

Move into the project folder.

```bash
cd InsightFlow_AI
```

---

## Backend Setup

Move to the backend folder.

```bash
cd backend
```
Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install the required packages.

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file inside the `backend` folder and add the following:

```env
GEMINI_API_KEY=your_api_key_here
AI_PROVIDER=gemini
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

Start the FastAPI server.

```bash
uvicorn app.main:app --reload
```

```bash
uvicorn app.main:app --reload
```

Backend API

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/api/docs
```

---

## Frontend Setup

Open another terminal.

Move into the frontend folder.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Start the development server.

```bash
npm run dev
```

Open the URL shown in the terminal (usually http://localhost:5173).

---

## Using the Application

1. Register a new account.
2. Log in to the application.
3. Upload a CSV or Excel dataset.
4. Explore dashboards and interactive charts.
5. View machine learning insights.
6. Ask business questions using the AI Copilot.
7. Download reports.

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

## Roadmap

Planned improvements include:

- Role-based authentication
- Real-time analytics
- Multiple database support
- Advanced forecasting models
- RAG-based document intelligence
- Export to PowerPoint and PDF
- Dashboard customization

---

## Contributing

Contributions, suggestions, and improvements are welcome. Feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Author

**Mahesh Damam**

GitHub: https://github.com/maheshdamam

