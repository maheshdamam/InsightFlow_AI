# InsightFlow AI

An enterprise-style AI Business Intelligence platform. Upload a CSV/Excel file, get it
auto-cleaned, see live KPIs/trends/charts, read AI-generated business insights and
recommendations, run ML models (customer segmentation, anomaly detection, forecasting),
export polished reports, manage users via an admin panel, and ask questions about your
data in plain English via an AI copilot with row-level retrieval (RAG).

This is a working full-stack app, not a toy demo — every feature below was built, run
against a real database, and tested end-to-end (not just import-checked) while building it.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Pandas, scikit-learn, XGBoost, Prophet, ChromaDB, JWT auth
- **Frontend:** React (Vite), Tailwind CSS, Recharts, d3-sankey, react-simple-maps, React Router
- **Database:** SQLite by default (zero setup), swap to PostgreSQL via one env var

## Quick start

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults work out of the box with SQLite
python -m app.create_db         # creates tables + a default admin user
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs
Default login: `admin@insightflow.ai` / `ChangeMe123!` — **change this immediately.**

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The dev server proxies `/api/*` to `localhost:8000`, so both
must be running.

### 3. Try it

1. Register or log in (the first registered user is a regular `viewer` — use
   `python -m app.create_db` or promote a user's `role` to `admin` directly in the DB to
   access the Admin panel).
2. Go to **Datasets → Upload** and drop in any sales-style CSV (needs at minimum a date,
   a revenue-like column, and ideally product/region/customer/category columns — column
   names are auto-detected by keyword, e.g. anything containing "revenue"/"sales"/"amount").
3. Go to **Dashboard** — three tabs: **Overview** (KPIs, trend, insights, recommendations),
   **More Charts** (heatmap, treemap, funnel, sankey, geo map), **ML Insights** (customer
   segments, anomaly detection).
4. Go to **AI Copilot** and ask things like "Which product should I discontinue?" or
   "What did Alice buy in March?" (the second kind of question is answered via row-level
   retrieval, not just aggregate stats).
5. Go to **Reports** to export the current dataset as PDF, Excel, or PowerPoint.
6. If you're an admin, go to **Admin** to manage users, see all datasets across the
   platform, and review the activity log.

A ready-made sample file to try this with:

```csv
date,category,product,region,revenue,profit,customer
2026-01-01,Electronics,Laptop,North,1000,200,Alice
2026-01-15,Electronics,Phone,South,500,50,Bob
2026-02-01,Electronics,Laptop,North,1200,240,Carol
2026-02-05,Electronics,Tablet,South,300,-20,Alice
2026-02-10,Electronics,Laptop,South,900,150,Dave
2026-03-01,Electronics,Phone,North,700,90,Erin
```

## What's implemented

| Feature | Status |
|---|---|
| JWT auth, RBAC (admin/analyst/viewer) | ✅ Working |
| Upload, validate, auto-clean CSV/Excel | ✅ Working (dedup, missing values, outlier flagging, date/text normalization, multi-encoding fallback) |
| Dataset versioning, rename, delete | ✅ Working |
| KPIs, revenue trend, breakdowns by product/region/customer | ✅ Working, via heuristic column-mapping |
| Business insights (best/worst product, top/weak region, loss-makers) | ✅ Working |
| Rule-based recommendation engine | ✅ Working |
| Forecasting: Prophet + XGBoost (lag/day-of-week features) + linear fallback | ✅ Working — pick the model via the `model` field on `/ai/forecast` |
| Customer segmentation (K-Means on RFM) | ✅ Working |
| Anomaly detection (Isolation Forest) | ✅ Working |
| More chart types: heatmap, treemap, funnel, sankey, geo map | ✅ Working |
| Reports export: PDF, Excel (multi-sheet), PowerPoint (native charts) | ✅ Working |
| Admin panel: user management, cross-user dataset overview, activity log, system stats | ✅ Working |
| AI Copilot with RAG (TF-IDF row-level retrieval + stat grounding) | ✅ Working — see note below |
| AI Copilot LLM backend (Ollama or OpenAI) | ✅ Working, needs a local Ollama server or an OpenAI key — without either, it still returns the retrieved rows and stats, just without a generated natural-language answer |

## Notes on specific design choices

- **RAG uses TF-IDF, not a downloaded embedding model.** Chroma's default embedding
  function downloads a MiniLM model from an S3 bucket on first use — a fragile dependency
  that silently fails behind restrictive networks. Instead, `app/ai/vector_store.py` fits a
  local TF-IDF vectorizer per dataset and passes precomputed vectors into Chroma. This is
  fully local and deterministic, and handles the copilot's example questions well (matching
  customer names, products, regions, etc.) without needing internet access at query time.
  If you want true semantic embeddings later, swap the vectorizer for
  `sentence-transformers` and pass real embeddings the same way.
- **Prophet forecasting requires a working cmdstan backend**, which `pip install prophet`
  doesn't always set up automatically (it depends on your platform/network). If Prophet
  fails to fit, forecasting automatically falls back to XGBoost-style linear regression, so
  the feature never breaks — but for the full seasonal-forecasting benefit, you may need to
  run `python -m cmdstanpy.install_cmdstan` once after installing dependencies.
- **`posthog==2.5.0` is pinned** in requirements.txt purely to silence a harmless telemetry
  warning from a version mismatch with `chromadb==0.5.5` — doesn't affect functionality.

## Extending this

- **Column mapping overrides:** `analytics.guess_column_mapping()` is heuristic; if it
  guesses wrong for an unusual dataset, add a manual-override endpoint that stores a
  mapping per dataset instead of re-guessing every request.
- **RAG at scale:** `vector_store.py` indexes up to 3,000 raw rows per dataset. For larger
  datasets, index daily/weekly aggregates instead of individual rows so retrieval scales
  sublinearly.
- **Postgres:** set `DATABASE_URL=postgresql://user:pass@host:5432/dbname` in `.env`, then
  `alembic upgrade head` instead of `create_db.py` for real migrations.
- **Still not built:** email verification/forgot-password, websocket/email notifications,
  dark mode. These are lower-value additions — see the chat history for why they were
  deprioritized.

## Project layout

Matches the structure in the original spec: `backend/app/{routes,services,models,schemas,
crud,ml,ai,utils}`, `frontend/src/{components,charts,pages,hooks,services,utils}`, plus
top-level `datasets/`, `reports/`, `screenshots/`. New this round: `backend/app/ai/
vector_store.py` (RAG), `backend/app/services/reports.py` (exports),
`backend/app/services/chart_data.py` (new chart types), `backend/app/ml/segmentation.py`
+ `anomaly.py` (ML models), `backend/app/routes/admin.py` (admin panel), `backend/
vector_store/` (per-dataset Chroma indices, gitignored).
