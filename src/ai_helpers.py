from __future__ import annotations

import ast
import os
import re
from pathlib import Path

import google.generativeai as genai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed_data.csv"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

SEARCH_COLUMNS = [
    "ten_cong_viec",
    "ten_cong_ty",
    "muc_luong",
    "dia_chi",
    "nganh_nghe",
    "nam_kinh_nghiem",
    "cap_bac",
    "loai_hinh",
    "loai_hop_dong",
    "cong_nghe_su_dung",
    "mo_ta_cong_viec",
    "nhom_cong_viec",
]


def parse_list_like(value: object) -> str:
    if value is None:
        return "N/A"
    if pd.api.types.is_scalar(value) and pd.isna(value):
        return "N/A"

    text = str(value).strip()
    if not text or text in {"[]", "['']"}:
        return "N/A"

    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return text

        if isinstance(parsed, list):
            cleaned_items = [str(item).strip() for item in parsed if str(item).strip()]
            return ", ".join(cleaned_items) if cleaned_items else "N/A"

    return text


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_for_search(text: str) -> str:
    lowered = _clean_whitespace(text).lower()
    return re.sub(r"[^a-z0-9\s]", " ", lowered)


@st.cache_data(show_spinner=False)
def load_processed_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    return pd.read_csv(DATA_PATH).fillna("")


def _build_search_blob(row: pd.Series) -> str:
    values = [parse_list_like(row.get(column, "")) for column in SEARCH_COLUMNS]
    return _normalize_for_search(" ".join(values))


def _build_job_label(row: pd.Series, row_index: int) -> str:
    job_title = str(row.get("ten_cong_viec", "Unknown role")).strip() or "Unknown role"
    company = str(row.get("ten_cong_ty", "Unknown company")).strip() or "Unknown company"
    location = parse_list_like(row.get("dia_chi", "N/A"))
    return f"{job_title} | {company} | {location} [#{row_index}]"


@st.cache_data(show_spinner=False)
def load_indexed_jobs() -> pd.DataFrame:
    indexed = load_processed_data().copy()
    indexed["search_blob"] = indexed.apply(_build_search_blob, axis=1)
    indexed["job_label"] = [
        _build_job_label(row, row_index)
        for row_index, row in indexed.iterrows()
    ]
    return indexed


def retrieve_relevant_jobs(query: str, indexed_jobs: pd.DataFrame, top_k: int = 6) -> pd.DataFrame:
    normalized_query = _normalize_for_search(query)
    query_terms = [term for term in normalized_query.split() if len(term) > 1]
    if not query_terms:
        return indexed_jobs.iloc[0:0].copy()

    scores: list[tuple[int, int]] = []
    for row_idx, blob in indexed_jobs["search_blob"].items():
        if not blob:
            continue
        matched_terms = sum(1 for term in query_terms if term in blob)
        if matched_terms == 0:
            continue
        frequency_bonus = sum(blob.count(term) for term in query_terms)
        score = matched_terms * 3 + frequency_bonus
        scores.append((row_idx, score))

    if not scores:
        return indexed_jobs.iloc[0:0].copy()

    scores.sort(key=lambda item: item[1], reverse=True)
    selected_indices = [row_idx for row_idx, _ in scores[:top_k]]
    return indexed_jobs.loc[selected_indices].copy()


def _short_text(value: object, max_len: int = 320) -> str:
    cleaned = _clean_whitespace(parse_list_like(value))
    if len(cleaned) <= max_len:
        return cleaned
    return f"{cleaned[:max_len - 3]}..."


def format_jobs_for_prompt(job_rows: pd.DataFrame, max_items: int = 6, max_chars: int = 7000) -> str:
    if job_rows.empty:
        return "No matching rows were found in processed_data.csv."

    chunks: list[str] = []
    current_length = 0

    for display_index, (_, row) in enumerate(job_rows.head(max_items).iterrows(), start=1):
        chunk = "\n".join(
            [
                f"[Job {display_index}]",
                f"- Title: {_short_text(row.get('ten_cong_viec', 'N/A'), 120)}",
                f"- Company: {_short_text(row.get('ten_cong_ty', 'N/A'), 120)}",
                f"- Salary: {_short_text(row.get('muc_luong', 'N/A'), 80)}",
                f"- Location: {_short_text(row.get('dia_chi', 'N/A'), 160)}",
                f"- Experience: {_short_text(row.get('nam_kinh_nghiem', 'N/A'), 40)}",
                f"- Levels: {_short_text(row.get('cap_bac', 'N/A'), 120)}",
                f"- Skills/Tech: {_short_text(row.get('cong_nghe_su_dung', 'N/A'), 240)}",
                f"- Job Group: {_short_text(row.get('nhom_cong_viec', 'N/A'), 120)}",
                f"- Description: {_short_text(row.get('mo_ta_cong_viec', 'N/A'), 420)}",
                f"- URL: {_short_text(row.get('url', 'N/A'), 220)}",
            ]
        )
        if current_length + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        current_length += len(chunk)

    if not chunks:
        return "No matching rows were found in processed_data.csv."

    return "\n\n".join(chunks)


def format_job_for_display(job_row: pd.Series) -> str:
    return "\n".join(
        [
            f"**Job title:** {parse_list_like(job_row.get('ten_cong_viec', 'N/A'))}",
            f"**Company:** {parse_list_like(job_row.get('ten_cong_ty', 'N/A'))}",
            f"**Salary range:** {parse_list_like(job_row.get('muc_luong', 'N/A'))}",
            f"**Location:** {parse_list_like(job_row.get('dia_chi', 'N/A'))}",
            f"**Experience (years):** {parse_list_like(job_row.get('nam_kinh_nghiem', 'N/A'))}",
            f"**Tech stack:** {parse_list_like(job_row.get('cong_nghe_su_dung', 'N/A'))}",
            f"**Job level:** {parse_list_like(job_row.get('cap_bac', 'N/A'))}",
        ]
    )


def build_job_option_map(indexed_jobs: pd.DataFrame) -> dict[str, int]:
    return {row["job_label"]: row_idx for row_idx, row in indexed_jobs.iterrows()}


@st.cache_resource(show_spinner=False)
def get_gemini_model(model_name: str | None = None) -> genai.GenerativeModel:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")

    selected_model = model_name or os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_GEMINI_MODEL
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(selected_model)


def generate_gemini_text(prompt: str, model_name: str | None = None, temperature: float = 0.3) -> str:
    model = get_gemini_model(model_name=model_name)
    response = model.generate_content(prompt, generation_config={"temperature": temperature})

    response_text = getattr(response, "text", None)
    if response_text:
        return response_text.strip()

    candidates = getattr(response, "candidates", None)
    if candidates:
        extracted_parts: list[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) if content else None
            if not parts:
                continue
            for part in parts:
                part_text = getattr(part, "text", "")
                if part_text:
                    extracted_parts.append(part_text)
        if extracted_parts:
            return "\n".join(extracted_parts).strip()

    raise RuntimeError("Gemini returned an empty response.")
