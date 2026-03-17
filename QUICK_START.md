# Quick Start - What You Need to Know

## 🎯 What This Project Does

**Job Market Analytics** = End-to-end intelligence platform for IT job market in Vietnam

**Pipeline**: Crawl TopDev → Clean Data → Predict Salaries → Recommend Jobs → Show Dashboard

**Users**: Job seekers (find roles), employers (market insights), data analysts (raw data)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TopDev.vn (Website)                                               │
│       ↓                                                             │
│  [Selenium Crawler] → topdev_crawler_save_time.ipynb              │
│       ↓                                                             │
│  CSV Backups (30+ daily snapshots in /csv_backup/)                │
│       ↓                                                             │
│  [Data Consolidation] → Load all CSVs, concatenate                │
│       ↓                                                             │
│  [Preprocessing] → topdev_preprocess_job_cluster.ipynb            │
│       ├─ Parse salary ranges (currency convert to USD)            │
│       ├─ Translate job titles (Vietnamese → English)              │
│       └─ Cluster jobs into 5 categories                           │
│       ↓                                                             │
│  processed_data.csv ← **Main dataset** (single source of truth)   │
│       ├→ MongoDB Atlas (backup)                                   │
│       ├→ Streamlit App (live)                                     │
│       └→ Model evaluation (accuracy check)                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Streamlit App (app.py) — 4 tabs:                                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Tab 1: Dashboard                                           │  │
│  │  └─ MongoDB Charts iframe (industry trends, salary bands)  │  │
│  │    Files: dashboard.py                                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Tab 2: Recommendation Engine                               │  │
│  │  ├─ User inputs keywords (skill, location, company, etc.)  │  │
│  │  ├─ Filter jobs matching ALL keywords                      │  │
│  │  ├─ Rank by weighted similarity score                      │  │
│  │  └─ Display top-N results                                  │  │
│  │    Files: recommendation.py (155 lines)                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Tab 3: Q&A Chatbot                                         │  │
│  │  ├─ User asks question about job market                    │  │
│  │  ├─ Send processed_data.csv + question to HuggingFace LLM  │  │
│  │  └─ Return LLM response (DeepSeek-V3.2 model)            │  │
│  │    Files: chatbot.py (72 lines)                            │  │
│  │    API: HuggingFace Inference                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Tab 4: Feature Lab                                         │  │
│  │  ├─ Select job from dataset                                │  │
│  │  ├─ [BUTTON 1] Predict Salary                              │  │
│  │  │    └─ Send job details to Gemini AI                     │  │
│  │  │        → Get salary range (e.g., "$100K - $150K")       │  │
│  │  └─ [BUTTON 2] Get Interview Advice                        │  │
│  │       └─ Send job + candidate description to Gemini        │  │
│  │           → Get career advice                               │  │
│  │    Files: feature.py (241 lines)                            │  │
│  │    API: Google Gemini (gemini-2.5-flash)                   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Organization

```
Job-Market-Analytics/
├── app.py                                    (44 lines) Main entry
├── dashboard.py                              (29 lines) Tab 1
├── recommendation.py                         (155 lines) Tab 2
├── chatbot.py                                (72 lines) Tab 3
├── feature.py                                (241 lines) Tab 4
├── test.py                                   (minimal test)
│
├── topdev_crawler_save_time.ipynb            Crawl TopDev (11 cells)
├── topdev_preprocess_all_in_one.ipynb        Data clean v1 (17 cells)
├── topdev_preprocess_job_cluster.ipynb       Data clean v2 - PRIMARY (25 cells)
├── topdev_model_preparation.ipynb            Feature eng (20 cells)
├── topdev_evaluate_salary_model.ipynb        Model eval (17 cells)
│
├── topdev/                                   (older version of notebooks)
│   ├── topdev_crawler.ipynb
│   ├── topdev_preprocess.ipynb
│   ├── Preprocessing.ipynb
│   └── topdev_crawler_save_time.ipynb
│
├── csv_backup/                               (30+ historical snapshots)
│   └── topdev_YYYYMMDD.csv
│
├── processed_data.csv                        ← **Main dataset**
│
├── requirements.txt                          (dependencies)
├── .env.example                              (config template)
├── README.md                                 (project setup)
└── PROJECT_SUMMARY.md                        (STAR format)
```

---

## 🔴 Critical Issues Found

### Security (CRITICAL — Fix Immediately)
1. **Gemini API key hardcoded** in `feature.py` line 9
2. **MongoDB credentials** in 4 notebooks
3. **GitHub password** in crawler notebook
4. **HuggingFace key** in model prep notebook

**Action**: Move all to `.env` file (see `chatbot.py` as correct example)

### Code Quality (HIGH)
5. **Data loading duplicated 4 times** (identical 40-line code blocks in all notebooks)
6. **No error handling** (app crashes if any API fails)
7. **Predictions ephemeral** (model eval results not saved)
8. **Notebook logic only** (can't reproduce 6 months later)

### Performance (MEDIUM)
9. **Entire CSV sent to LLM** (chatbot sends full dataset as context)
10. **Naive string matching** (recommendation engine is O(n))
11. **No caching** (expensive API calls repeated)

---

## 📊 Data Flow Example

### Input
```
User asks: "Find Python jobs in Ho Chi Minh with 2-3 years experience"
```

### Processing
```
1. Recommendation Engine filters: 
   - Contains "Python" → 200 jobs
   - Location includes "HCM" → 50 jobs
   - Experience 2-3 years → 20 jobs

2. Rank by weights:
   - Job title: 10x weight
   - Location: 10x weight
   - Tech stack: 10x weight
   - Company size: 2x weight
   - ... (12 total features)

3. Sort by match score (highest first)
```

### Output
```
Top 5 jobs:
┌─────────────────────────────────────────┐
│ Python Backend Developer (FPT Software) │ Match: 95%
│ Senior Python Engineer (Tiki)           │ Match: 92%
│ Data Engineer - Python (Viettel)        │ Match: 88%
│ ... (more results)
└─────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Scraping** | Selenium | Crawl TopDev.vn (dynamic content) |
| **Data Processing** | Pandas, NumPy, Regex | Clean, normalize salary/experience/titles |
| **Data Translation** | deep_translator | Vietnamese → English job titles |
| **UI Framework** | Streamlit | Web app (4 tabs) |
| **Database** | MongoDB Atlas | Backup + persistence |
| **Salary Prediction** | Google Gemini API | Generative AI (LLM) |
| **Chatbot** | HuggingFace Inference | DeepSeek-V3.2 model |
| **Visualization** | MongoDB Charts | Embedded dashboard |
| **Recommendation** | Custom algorithm | Content-based filtering with weights |

---

## 🎯 How to Use This Project

### For Job Seekers
1. Open Streamlit app
2. Go to "Recommendation" tab
3. Enter keywords (Python, Remote, $50K+, etc.)
4. Get ranked job matches

### For Data Analysts
1. Export `processed_data.csv`
2. Analyze salary trends by location/skill/company
3. Dashboard tab shows pre-built visualizations

### For Developers
1. Run crawl: `topdev_crawler_save_time.ipynb`
2. Preprocess: `topdev_preprocess_job_cluster.ipynb`
3. Deploy app: `streamlit run app.py`

---

## ⚡ Next Steps (Priority Order)

1. **TODAY**: Read `EXEC_SUMMARY.md` (this file + overview)
2. **THIS WEEK**: 
   - Read full `ANALYSIS_REPORT.md` (detailed breakdown)
   - Rotate all exposed API keys
   - Move secrets to `.env`
3. **NEXT 2 WEEKS**: 
   - Consolidate data loading (DRY)
   - Add error handling
   - Convert critical notebooks to Python modules
4. **WEEKS 3-6**: 
   - Implement remaining improvements from checklist
   - Set up CI/CD pipeline
   - Create KPI dashboard

---

## 📞 Common Questions

**Q: How often is data refreshed?**  
A: Currently manual (whenever someone runs preprocessing notebook). Should be automated weekly.

**Q: What if an API goes down?**  
A: App crashes. Need error handling + fallbacks.

**Q: Can I reproduce results 6 months later?**  
A: NO (notebook-only logic). Need to convert to modules first.

**Q: Why is salary prediction using Gemini, not a traditional ML model?**  
A: Because it's a capstone project (Gen-AI is trendy). Should benchmark vs. XGBoost to validate if it's worth the cost.

**Q: How much does this cost to run?**  
A: Depends on API usage:
- Google Gemini: ~$0.10 per 1000 predictions
- HuggingFace: ~$0.001 per query
- MongoDB: ~$57/month (Atlas M0 free tier)

---

## 📖 Document Guide

| Document | Read When | Purpose |
|----------|-----------|---------|
| **QUICK_START.md** (you are here) | First | High-level overview |
| **EXEC_SUMMARY.md** | Second | Key findings + roadmap |
| **ANALYSIS_REPORT.md** | Third | Deep technical analysis |
| **IMPROVEMENTS_CHECKLIST.md** | Implementation | Track progress |
| **README.md** | Setup | How to install & run |

---

## ✅ Success Criteria

After improvements are complete:

- ✅ No hardcoded secrets (all in `.env`)
- ✅ App doesn't crash (all errors handled)
- ✅ Pipeline reproducible (convert notebooks to modules)
- ✅ Predictions tracked (audit trail)
- ✅ Performance optimized (RAG chatbot, TF-IDF recommendations)
- ✅ Model benchmarked (Gemini vs. XGBoost vs. baseline)
- ✅ Fully documented (architecture, runbook, data dictionary)
- ✅ CI/CD pipeline (weekly data refresh)
- ✅ KPI dashboard (business metrics)
- ✅ Production-ready (8/10 score)

