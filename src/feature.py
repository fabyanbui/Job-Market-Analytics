import pandas as pd
import streamlit as st
from google.api_core.exceptions import GoogleAPIError

from ai_helpers import (
    format_job_for_display,
    format_jobs_for_prompt,
    generate_gemini_text,
    load_indexed_jobs,
    parse_list_like,
    retrieve_relevant_jobs,
)


def _build_fit_prompt(selected_job_context: str, market_context: str, candidate_profile: str) -> str:
    return f"""
You are an experienced career coach for Vietnam's technology job market.
Use only the provided dataset context.

Deliver a markdown answer with this structure:
1) Fit score (0-100) + 2-3 sentence justification
2) Strong matches (3 bullet points)
3) Skill/experience gaps (3 bullet points)
4) 30-day action plan (week-by-week)
5) Specific suggestions to improve interview readiness

If dataset context is insufficient, state that explicitly before giving cautious guidance.

[Selected Job]
{selected_job_context}

[Related Market Context]
{market_context}

[Candidate Profile]
{candidate_profile}
"""


def _build_interview_prompt(
    selected_job_context: str,
    market_context: str,
    candidate_background: str,
    interview_focus: str,
    number_of_questions: int,
) -> str:
    return f"""
You are a senior technical interviewer and hiring manager.
Create interview preparation material grounded in the dataset context.

Requirements:
- Generate exactly {number_of_questions} interview questions.
- Focus mode: {interview_focus}.
- For each question include:
  - Why interviewer asks it
  - What a strong answer should cover
  - A short sample answer outline
- Include 5 smart questions that the candidate should ask the interviewer.
- Keep response in clean markdown.

[Selected Job]
{selected_job_context}

[Related Market Context]
{market_context}

[Candidate Background]
{candidate_background if candidate_background.strip() else "Not provided"}
"""


def _build_job_selection_table(indexed_jobs: pd.DataFrame) -> pd.DataFrame:
    table = indexed_jobs.reset_index().rename(columns={"index": "row_index"}).copy()
    table["Job title"] = table["ten_cong_viec"].astype(str)
    table["Company"] = table["ten_cong_ty"].astype(str)
    table["Salary"] = table["muc_luong"].astype(str)
    table["Location"] = table["dia_chi"].apply(parse_list_like)
    table["Experience"] = table["nam_kinh_nghiem"].astype(str)
    table["Tech stack"] = table["cong_nghe_su_dung"].apply(parse_list_like)
    return table[
        [
            "row_index",
            "Job title",
            "Company",
            "Salary",
            "Location",
            "Experience",
            "Tech stack",
        ]
    ]


def tab_4():
    st.header("Feature")
    st.caption("Gemini-powered tools: Job Fit Analyzer + Interview Prep Generator")

    try:
        indexed_jobs = load_indexed_jobs()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    if indexed_jobs.empty:
        st.warning("No jobs found in processed_data.csv.")
        return

    if "feature_selected_job_idx" not in st.session_state:
        st.session_state.feature_selected_job_idx = int(indexed_jobs.index[0])

    st.write("Select one row in the table to choose the target job posting.")
    selection_table = _build_job_selection_table(indexed_jobs).reset_index(drop=True)
    current_selected_idx = st.session_state.feature_selected_job_idx
    if current_selected_idx not in selection_table["row_index"].values:
        current_selected_idx = int(selection_table.iloc[0]["row_index"])
        st.session_state.feature_selected_job_idx = current_selected_idx

    default_selected_position = int(
        selection_table.index[selection_table["row_index"] == current_selected_idx][0]
    )
    editor_table = selection_table.drop(columns=["row_index"]).copy()
    editor_table.insert(0, "Select", False)
    editor_table.loc[default_selected_position, "Select"] = True

    edited_table = st.data_editor(
        editor_table,
        use_container_width=True,
        hide_index=True,
        key="feature_job_selection_table",
        disabled=[column for column in editor_table.columns if column != "Select"],
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Tick one row to select the target job.",
            )
        },
    )

    selected_rows = edited_table.index[edited_table["Select"]].tolist()
    if not selected_rows:
        selected_table_idx = default_selected_position
    elif len(selected_rows) > 1:
        alternative_rows = [row_idx for row_idx in selected_rows if row_idx != default_selected_position]
        selected_table_idx = int(alternative_rows[0] if alternative_rows else selected_rows[0])
        st.info("Multiple rows selected. Using the newly selected row.")
    else:
        selected_table_idx = int(selected_rows[0])

    st.session_state.feature_selected_job_idx = int(selection_table.iloc[selected_table_idx]["row_index"])

    selected_idx = st.session_state.feature_selected_job_idx
    if selected_idx not in indexed_jobs.index:
        selected_idx = int(indexed_jobs.index[0])
        st.session_state.feature_selected_job_idx = selected_idx

    selected_job = indexed_jobs.loc[selected_idx]
    selected_job_df = indexed_jobs.loc[[selected_idx]]

    st.caption(
        f"Selected job: **{selected_job.get('ten_cong_viec', 'N/A')}** at "
        f"**{selected_job.get('ten_cong_ty', 'N/A')}**"
    )

    with st.expander("Selected job details", expanded=False):
        st.markdown(format_job_for_display(selected_job))
        job_url = str(selected_job.get("url", "")).strip()
        if job_url:
            st.markdown(f"[Open job posting]({job_url})")

    st.markdown("---")
    st.subheader("1) Job Fit Analyzer")
    st.write("Paste your profile/CV summary to estimate fit against the selected job.")
    candidate_profile = st.text_area(
        "Candidate profile",
        height=150,
        key="job_fit_candidate_profile",
        placeholder="Example: 3 years Python backend, FastAPI, PostgreSQL, AWS, Docker...",
    )

    if st.button("Analyze fit with Gemini", key="analyze_fit_button"):
        if not candidate_profile.strip():
            st.warning("Please provide a candidate profile first.")
        else:
            related_jobs = retrieve_relevant_jobs(
                f"{selected_job.get('ten_cong_viec', '')} {candidate_profile}",
                indexed_jobs,
                top_k=5,
            )
            context_jobs = pd.concat([selected_job_df, related_jobs], axis=0).drop_duplicates()
            selected_job_context = format_jobs_for_prompt(selected_job_df, max_items=1, max_chars=2500)
            market_context = format_jobs_for_prompt(context_jobs, max_items=5, max_chars=6000)
            fit_prompt = _build_fit_prompt(selected_job_context, market_context, candidate_profile)

            with st.spinner("Evaluating candidate fit..."):
                try:
                    fit_result = generate_gemini_text(fit_prompt, temperature=0.3)
                    st.markdown(fit_result)
                except (GoogleAPIError, ValueError, RuntimeError) as exc:
                    st.error(f"Gemini request failed: {exc}")

    st.markdown("---")
    st.subheader("2) Interview Prep Generator")
    st.write("Generate tailored interview questions and answer strategy for the selected role.")
    candidate_background = st.text_area(
        "Optional candidate background",
        height=120,
        key="interview_candidate_background",
        placeholder="Example: Strong in SQL and data pipelines, weaker in system design...",
    )
    interview_focus = st.selectbox(
        "Interview focus",
        options=[
            "Balanced",
            "Technical-heavy",
            "Behavioral-heavy",
            "System design-heavy",
        ],
        key="interview_focus_mode",
    )
    number_of_questions = st.slider(
        "Number of interview questions",
        min_value=5,
        max_value=12,
        value=8,
        key="interview_question_count",
    )

    if st.button("Generate interview prep with Gemini", key="interview_prep_button"):
        related_jobs = retrieve_relevant_jobs(str(selected_job.get("ten_cong_viec", "")), indexed_jobs, top_k=4)
        selected_job_context = format_jobs_for_prompt(selected_job_df, max_items=1, max_chars=2500)
        market_context = format_jobs_for_prompt(related_jobs, max_items=4, max_chars=4500)
        interview_prompt = _build_interview_prompt(
            selected_job_context,
            market_context,
            candidate_background,
            interview_focus,
            number_of_questions,
        )

        with st.spinner("Generating interview prep package..."):
            try:
                interview_result = generate_gemini_text(interview_prompt, temperature=0.35)
                st.markdown(interview_result)
            except (GoogleAPIError, ValueError, RuntimeError) as exc:
                st.error(f"Gemini request failed: {exc}")
