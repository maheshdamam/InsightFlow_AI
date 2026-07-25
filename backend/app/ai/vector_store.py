"""
Row-level retrieval for the AI Copilot (RAG).

Design choice: Chroma's *default* embedding function downloads a MiniLM ONNX
model from an external bucket on first use. That's a fragile runtime
dependency — it fails silently behind restrictive firewalls/proxies, which
defeats the point of a "just works locally" feature. Instead, we compute our
own embeddings with a TF-IDF vectorizer (scikit-learn, already a dependency,
fully local, deterministic) and pass precomputed vectors into Chroma. This
gives real semantic-ish retrieval (shared vocabulary/context matches) without
any network dependency at index or query time.

Each dataset gets its own persistent Chroma collection plus a pickled
TF-IDF vectorizer (must reuse the exact same fitted vectorizer for queries
as was used for indexing, since vector dimensions must match).
"""
from __future__ import annotations

import os
import pickle
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vector_store")
MAX_ROWS_INDEXED = 3000  # keeps indexing fast; see note in index_dataset() for scaling beyond this

_CHROMA_SETTINGS = ChromaSettings(anonymized_telemetry=False)


def _chroma_client(dataset_id: str) -> "chromadb.ClientAPI":
    return chromadb.PersistentClient(path=_persist_dir(dataset_id), settings=_CHROMA_SETTINGS)


def _persist_dir(dataset_id: str) -> str:
    path = os.path.join(VECTOR_STORE_DIR, dataset_id)
    os.makedirs(path, exist_ok=True)
    return path


def _vectorizer_path(dataset_id: str) -> str:
    return os.path.join(_persist_dir(dataset_id), "vectorizer.pkl")


def _row_to_document(row: pd.Series, mapping: Dict[str, Optional[str]]) -> str:
    """Turn one row into a short natural-language sentence for embedding/retrieval."""
    parts = []
    for concept in ("date", "customer", "product", "category", "region"):
        col = mapping.get(concept)
        if col and col in row.index and pd.notna(row[col]):
            parts.append(f"{concept}: {row[col]}")
    for concept in ("revenue", "profit", "quantity"):
        col = mapping.get(concept)
        if col and col in row.index and pd.notna(row[col]):
            parts.append(f"{concept}: {row[col]}")
    return ", ".join(parts) if parts else " ".join(str(v) for v in row.values)


def index_dataset(dataset_id: str, df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> int:
    """
    Build (or rebuild) the vector index for a dataset. Called once after
    upload/cleaning. For datasets larger than MAX_ROWS_INDEXED, only the most
    recent rows (by date, if available) are indexed — for a production system
    with very large datasets, switch to indexing daily/weekly aggregates
    instead of raw rows so retrieval scales sublinearly with row count.
    """
    work = df.copy()
    date_col = mapping.get("date")
    if date_col and date_col in work.columns:
        work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
        work = work.sort_values(date_col, ascending=False)
    work = work.head(MAX_ROWS_INDEXED)

    documents = [_row_to_document(row, mapping) for _, row in work.iterrows()]
    ids = [str(i) for i in work.index.tolist()]

    if not documents:
        return 0

    vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
    embeddings = vectorizer.fit_transform(documents).toarray().tolist()

    with open(_vectorizer_path(dataset_id), "wb") as f:
        pickle.dump(vectorizer, f)

    client = _chroma_client(dataset_id)
    # Recreate the collection fresh each time so re-uploads/re-indexing don't
    # accumulate stale rows from a previous version of the dataset.
    try:
        client.delete_collection("rows")
    except Exception:
        pass
    collection = client.create_collection("rows")
    collection.add(ids=ids, documents=documents, embeddings=embeddings)

    return len(documents)


def retrieve_relevant_rows(dataset_id: str, question: str, top_k: int = 8) -> List[str]:
    """Returns the top-k most relevant row documents for a question, or [] if not indexed."""
    vectorizer_path = _vectorizer_path(dataset_id)
    if not os.path.exists(vectorizer_path):
        return []

    try:
        with open(vectorizer_path, "rb") as f:
            vectorizer: TfidfVectorizer = pickle.load(f)

        query_embedding = vectorizer.transform([question]).toarray().tolist()

        client = _chroma_client(dataset_id)
        collection = client.get_collection("rows")
        results = collection.query(query_embeddings=query_embedding, n_results=min(top_k, collection.count() or 1))
        return results.get("documents", [[]])[0]
    except Exception:
        # Retrieval is an enhancement, not a hard requirement — if anything
        # goes wrong (corrupt index, dimension mismatch after re-indexing,
        # etc.) the copilot should still answer from stat-grounded context.
        return []


def is_indexed(dataset_id: str) -> bool:
    return os.path.exists(_vectorizer_path(dataset_id))
