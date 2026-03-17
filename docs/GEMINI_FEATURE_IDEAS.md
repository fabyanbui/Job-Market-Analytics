# Gemini Feature Ideas for `processed_data.csv`

## Goal
Extend the Streamlit app with Gemini-powered experiences that turn job postings into practical career intelligence.

## Already selected for implementation
1. **Job Fit Analyzer** (Tab 4)
2. **Interview Prep Generator** (Tab 4)

## Suggested next features

| Priority | Feature | What it does | Key columns used | Why it matters |
|---|---|---|---|---|
| High | Salary Benchmark Assistant | Compares selected role with similar jobs and explains realistic compensation range. | `muc_luong`, `ten_cong_viec`, `nam_kinh_nghiem`, `dia_chi`, `cong_nghe_su_dung` | Helps candidates negotiate with market-backed confidence. |
| High | Skill Gap Roadmap | Maps candidate profile to job requirements and proposes a 30/60/90-day learning plan. | `cong_nghe_su_dung`, `mo_ta_cong_viec`, `cap_bac`, `nhom_cong_viec` | Converts job descriptions into actionable upskilling plans. |
| Medium | Job Post Summarizer | Converts long job descriptions into concise sections (must-have skills, responsibilities, red flags). | `mo_ta_cong_viec`, `quy_trinh_phong_van`, `thong_tin_cong_ty` | Saves reading time and improves decision speed. |
| Medium | Company Snapshot Generator | Produces structured company brief for interview prep (culture hints, scale, role expectations). | `ten_cong_ty`, `quy_mo_cong_ty`, `quoc_tich_cong_ty`, `thong_tin_cong_ty` | Gives quick context before applications/interviews. |
| Medium | Resume Bullet Refiner | Turns user experience text into role-aligned bullet points based on selected jobs. | `ten_cong_viec`, `cong_nghe_su_dung`, `mo_ta_cong_viec`, `cap_bac` | Improves CV quality for ATS and recruiter review. |
| Low | Cover Letter Draft Assistant | Drafts targeted cover letters from selected posting + candidate profile. | `ten_cong_viec`, `ten_cong_ty`, `mo_ta_cong_viec` | Useful but less critical than interview/skill planning. |

## Implementation recommendations
1. Reuse one shared retrieval helper for all Gemini calls to keep responses grounded.
2. Keep a strict prompt policy: if context is weak, assistant must say so explicitly.
3. Cache dataset loading and avoid sending full CSV to Gemini each request.
4. Log prompt/response metadata (without PII) for quality monitoring.
5. Add optional bilingual output mode (Vietnamese/English) for user preference.
