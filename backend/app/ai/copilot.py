"""
AI Business Copilot.

Strategy: rather than sending the raw dataset to an LLM (slow, expensive,
often exceeds context limits), we compute a compact statistical summary of
the dataset (KPIs, top/bottom performers, trend direction) and pass THAT as
grounded context to the LLM along with the user's question. This keeps
answers fast, cheap, and factually tied to real numbers instead of the model
guessing.

On top of that stat grounding, we also retrieve the most relevant individual
rows via a local TF-IDF vector index (see app/ai/vector_store.py) so the
copilot can answer row-level questions ("show me orders from Alice in
March") that aggregate KPIs alone can't cover. Retrieval is additive and
best-effort — if a dataset hasn't been indexed yet (or indexing failed),
the copilot still works from stat-grounded context alone.

Supports two providers, switched via AI_PROVIDER in .env:
- "ollama": local LLM via Ollama (no API key needed, runs on your machine)
- "openai": OpenAI API (requires OPENAI_API_KEY)
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

import pandas as pd

from app.config import settings
from app.services.analytics import compute_kpis, business_insights, guess_column_mapping
from app.ai.vector_store import retrieve_relevant_rows

SYSTEM_PROMPT = """You are InsightFlow AI's Business Copilot, an assistant embedded in a \
business intelligence dashboard. You answer questions about the user's business data using \
ONLY the statistical context and retrieved rows provided below. Be concise, specific, and \
reference real numbers. If the context doesn't contain enough information to answer \
confidently, say so plainly instead of guessing.
"""


def _build_context(df: pd.DataFrame) -> Dict[str, Any]:
    mapping = guess_column_mapping(list(df.columns))
    return {
        "columns": list(df.columns),
        "row_count": len(df),
        "column_mapping_guess": mapping,
        "kpis": compute_kpis(df, mapping),
        "insights": business_insights(df, mapping),
    }


def _call_gemini(question: str, context: Dict[str, Any], retrieved_rows: List[str]) -> str:
    import json
    import requests

    retrieved_block = (
        "\n".join(f"- {row}" for row in retrieved_rows)
        if retrieved_rows
        else "(no specific rows retrieved for this question)"
    )

    prompt = f"""{SYSTEM_PROMPT}

Data Context:
{json.dumps(context, indent=2)}

Retrieved Rows (most relevant to the question):
{retrieved_block}

Question:
{question}
"""

    response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/generate",
        json={
            "model": "llama3.1:latest",
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]

def _call_gemini(question: str, context: Dict[str, Any], retrieved_rows: List[str]) -> str:
    import google.generativeai as genai

    retrieved_block = (
        "\n".join(f"- {row}" for row in retrieved_rows)
        if retrieved_rows
        else "(no specific rows retrieved for this question)"
    )

    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
{SYSTEM_PROMPT}

Data Context:
{json.dumps(context, indent=2)}

Retrieved Rows:
{retrieved_block}

Question:
{question}
"""

    response = model.generate_content(prompt)

    return response.text


def ask_copilot(df: pd.DataFrame, question: str, dataset_id: str = None) -> Dict[str, Any]:
    import traceback

    context = _build_context(df)
    retrieved_rows = (
        retrieve_relevant_rows(dataset_id, question, top_k=8)
        if dataset_id
        else []
    )

    try:
        answer = _call_gemini(question, context, retrieved_rows)

    except Exception as exc:
        print("\n" + "=" * 80)
        print("AI COPILOT ERROR")
        traceback.print_exc()
        print("=" * 80 + "\n")

        answer = (
            f"AI Error: {type(exc).__name__}\n\n"
            f"{str(exc)}"
        )

    return {
        "answer": answer,
        "supporting_data": {**context, "retrieved_rows": retrieved_rows},
    }