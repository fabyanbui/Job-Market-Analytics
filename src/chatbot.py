import pandas as pd
import streamlit as st
from google.api_core.exceptions import GoogleAPIError

from ai_helpers import (
    format_jobs_for_prompt,
    generate_gemini_text,
    load_indexed_jobs,
    parse_list_like,
    retrieve_relevant_jobs,
)

DEFAULT_ASSISTANT_MESSAGE = (
    "Hello! I am your Job Market Analytics assistant. "
    "Ask me anything about jobs inside `data/processed_data.csv`."
)


def _recent_chat_context(messages: list[dict[str, str]], max_turns: int = 3) -> str:
    clipped = messages[-(max_turns * 2) :]
    rows = []
    for message in clipped:
        role = "User" if message["role"] == "user" else "Assistant"
        rows.append(f"{role}: {message['content']}")
    return "\n".join(rows)


def _build_context_rows(matched_jobs: pd.DataFrame) -> list[dict[str, str]]:
    if matched_jobs.empty:
        return []

    preview_cols = [
        "ten_cong_viec",
        "ten_cong_ty",
        "muc_luong",
        "dia_chi",
        "cong_nghe_su_dung",
        "nganh_nghe",
    ]
    preview = matched_jobs[preview_cols].copy()
    for column in ["dia_chi", "cong_nghe_su_dung", "nganh_nghe"]:
        preview[column] = preview[column].apply(parse_list_like)
    preview = preview.rename(
        columns={
            "ten_cong_viec": "Job title",
            "ten_cong_ty": "Company",
            "muc_luong": "Salary",
            "dia_chi": "Location",
            "cong_nghe_su_dung": "Tech stack",
            "nganh_nghe": "Industry",
        }
    )
    return preview.reset_index(drop=True).to_dict(orient="records")


def _render_chat_history(messages: list[dict[str, str]]) -> None:
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            context_rows = message.get("context_rows", [])
            if context_rows:
                with st.expander("Show matched rows used as context"):
                    st.dataframe(pd.DataFrame(context_rows), use_container_width=True, hide_index=True)


def tab_3():
    st.header("Q&A")
    st.caption("Dataset-grounded chatbot powered by Gemini")

    try:
        indexed_jobs = load_indexed_jobs()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]

    if st.button("Clear chat", key="clear_chat_button"):
        st.session_state.qa_messages = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]
        st.rerun()

    _render_chat_history(st.session_state.qa_messages)

    question = st.chat_input("Example: Which Data Engineer jobs in Ho Chi Minh require Python?")
    if not question:
        return

    st.session_state.qa_messages.append({"role": "user", "content": question})

    matched_jobs = retrieve_relevant_jobs(question, indexed_jobs, top_k=6)
    data_context = format_jobs_for_prompt(matched_jobs, max_items=6, max_chars=6500)
    history_context = _recent_chat_context(st.session_state.qa_messages[:-1], max_turns=3)

    prompt = f"""
You are a senior data analyst assistant for the Vietnam IT job market.
Use only the dataset context below from processed_data.csv.

Rules:
- If the answer is not supported by dataset context, clearly say you do not have enough evidence.
- Never invent job postings, salary values, or companies that are not in context.
- If user asks for recommendations, cite concrete job title + company from context.
- Keep answers concise and actionable.
- Reply in the same language as the user question when possible.

[Recent Conversation]
{history_context}

[Dataset Context]
{data_context}

[User Question]
{question}
"""

    with st.spinner("Gemini is analyzing relevant jobs..."):
        try:
            answer = generate_gemini_text(prompt, temperature=0.2)
        except (GoogleAPIError, ValueError, RuntimeError) as exc:
            answer = (
                "I could not generate a reliable answer right now. "
                f"Gemini request failed: {exc}"
            )

    assistant_message = {"role": "assistant", "content": answer}
    context_rows = _build_context_rows(matched_jobs)
    if context_rows:
        assistant_message["context_rows"] = context_rows

    st.session_state.qa_messages.append(assistant_message)
    st.rerun()
