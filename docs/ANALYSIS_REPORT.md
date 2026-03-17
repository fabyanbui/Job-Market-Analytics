# Job Market Analytics - Comprehensive Repository Analysis

## EXECUTIVE SUMMARY

**Project Type**: University Capstone | Data Analytics + Gen-AI Application  
**Team Size**: 6 students  
**Core Tech Stack**: Python, Selenium, Pandas, Streamlit, MongoDB, Google Gemini API, HuggingFace API  
**Code Volume**: ~12,288 lines across 9 notebooks + 6 Python modules  
**Production Status**: Demo-stage with significant technical debt

---

## 1. CURRENT-STATE SUMMARY: DATA PIPELINE ARCHITECTURE

### 1.1 Pipeline Stages & Implementation

| Stage | Purpose | Input | Output | Implementation Files |
|-------|---------|-------|--------|----------------------|
| **CRAWL** | Collect IT jobs from TopDev.vn | TopDev.vn website (dynamic) | Raw CSV (multi-file) | `topdev_crawler_save_time.ipynb` |
| **PREPROCESS** | Clean, normalize, translate, cluster | CSV backup files in `/csv_backup/` | `processed_data.csv` | `topdev_preprocess_all_in_one.ipynb` <br> `topdev_preprocess_job_cluster.ipynb` |
| **MODEL/EVALUATE** | Train salary prediction using Gen-AI | `processed_data.csv` | Predictions, evaluation metrics | `topdev_model_preparation.ipynb` <br> `topdev_evaluate_salary_model.ipynb` |
| **APP/SERVE** | User-facing Streamlit dashboard | `processed_data.csv` + APIs | Live web application | `app.py`, `dashboard.py`, `recommendation.py`, `chatbot.py`, `feature.py` |

### 1.2 Data Artifacts & Flow

```
csv_backup/ (30+ historical snapshots)
    ↓
[topdev_preprocess_job_cluster.ipynb]
    ↓
processed_data.csv (single source of truth for app)
    ├─→ MongoDB Atlas (via cluster push)
    ├─→ [topdev_model_preparation.ipynb] 
    ├─→ [topdev_evaluate_salary_model.ipynb]
    └─→ Streamlit App (4 tabs)
            ├─ Tab 1: Dashboard (MongoDB Charts iframe)
            ├─ Tab 2: Recommendation Engine (keyword-based matching + weights)
            ├─ Tab 3: Q&A Chatbot (HuggingFace Mistral LLM)
            └─ Tab 4: Feature Lab (Gemini salary prediction + advice)
```

### 1.3 External Service Dependencies

| Service | Used In | Purpose | Risk Level |
|---------|---------|---------|-----------|
| **Google Gemini API** | `feature.py`, `topdev_evaluate_salary_model.ipynb` | Salary prediction, CV advice | HIGH (hardcoded key) |
| **HuggingFace Inference** | `chatbot.py` | Q&A bot (DeepSeek-V3.2) | HIGH (hardcoded key) |
| **MongoDB Atlas** | Preprocessing notebooks | Cloud data persistence | MEDIUM (hardcoded URI) |
| **Selenium WebDriver** | `topdev_crawler_save_time.ipynb` | Web scraping TopDev | HIGH (GitHub login automated) |
| **GitHub OAuth** | Crawler | TopDev authentication | MEDIUM (credentials in notebook) |
| **MongoDB Charts** | `dashboard.py` | Dashboard iframe embed | LOW (public link) |

### 1.4 Streamlit App Feature Mapping

**Tab 1: Dashboard**
- Embeds MongoDB Charts dashboard (hardcoded iframe URL)
- No data processing; pure visualization layer
- File: `dashboard.py` (29 lines)

**Tab 2: Recommendation**
- Takes multi-keyword input from user
- Filters jobs matching all keywords
- Ranks via weighted matching (10 features, weights hardcoded)
- File: `recommendation.py` (155 lines)
- Duplicated data transformation logic (appears also in `feature.py`)

**Tab 3: Q&A Chatbot**
- Loads `processed_data.csv` as context
- Sends CSV + user question to HuggingFace API (DeepSeek model)
- Chat history commented out (incomplete feature)
- File: `chatbot.py` (72 lines)

**Tab 4: Feature Lab**
- Select job → view details
- Button 1: "Predict Salary" → calls Gemini API
- Button 2: "Get Advice" → calls Gemini with job + candidate description
- PDF generation commented out
- File: `feature.py` (241 lines)

---

## 2. NOTEBOOK DEEP-DIVE

### 2.1 `topdev_crawler_save_time.ipynb` (11 code cells)

**Purpose**: Automated web scraping of TopDev job listings using Selenium

**Key Steps**:
1. GitHub login automation (hardcoded email: `mathonline03@gmail.com`)
2. Navigate to TopDev job portal
3. Infinite scroll to load all jobs
4. Parse job cards with CSS selectors
5. Export to CSV with 20 columns

**Outputs**: Raw CSV file (unnamed, likely saved with timestamp)

**Issues**:
- ⚠️ **CRITICAL**: GitHub credentials hardcoded (email + password visible in cells)
- No error handling for rate limiting or network timeouts
- Anti-bot detection not addressed (Selenium easily detected)
- No pagination logic; relies on hardcoded scroll time

---

### 2.2 `topdev_preprocess_all_in_one.ipynb` (17 code cells)

**Purpose**: Data cleaning and exploratory analysis

**Key Steps**:
1. Load all CSVs from `/csv_backup/`, concatenate
2. Replace `[]` with `['Thương lượng']` for missing salaries
3. Parse stringified Python lists in columns
4. Extract single element from list-columns
5. Clean salary ranges, experience years, company sizes
6. Push to MongoDB Atlas (via PyMongo)

**Outputs**: Cleaned data pushed to MongoDB, no CSV export

**Issues**:
- ⚠️ **CRITICAL**: MongoDB URI hardcoded with credentials
- No data validation or schema enforcement
- Duplicated salary extraction logic (also in `topdev_model_preparation.ipynb`)
- No data quality metrics reported

---

### 2.3 `topdev_preprocess_job_cluster.ipynb` (25 code cells) — **PRIMARY PREPROCESSING**

**Purpose**: Main data pipeline; produces `processed_data.csv`

**Key Steps**:
1. Load all CSVs from `/csv_backup/`, concatenate (DUPLICATE of preprocess_all_in_one)
2. Parse stringified lists
3. Extract salary ranges (min/max in USD)
4. **Translate job titles from Vietnamese to English** using `deep_translator`
5. **Cluster job titles into 5 standard groups** (Software Dev, Web Dev, Data/AI, DevOps, Mobile)
6. Normalize company sizes (Small, Medium, Large, Enterprise)
7. Extract experience years as integers
8. **Push to MongoDB Atlas**
9. Export deduplicated CSV as `processed_data.csv` ← **used by app & model notebooks**

**Outputs**: `processed_data.csv` (main dataset for app), MongoDB collection

**Unique Features**:
- Translation layer (Vietnamese → English job titles)
- Job clustering via heuristic matching (keywords)
- Deduplication by URL

**Issues**:
- ⚠️ **CRITICAL**: MongoDB URI hardcoded (same in 3 other notebooks)
- Salary extraction fragile (hardcoded currency conversion rates?)
- Translation API calls unthrottled (rate limit risk)
- Job clustering rules hardcoded; not ML-driven
- No logging or monitoring of pipeline steps

---

### 2.4 `topdev_model_preparation.ipynb` (20 code cells)

**Purpose**: Feature engineering for salary prediction model

**Key Steps**:
1. Load & preprocess data (DUPLICATE entire data loading logic)
2. Prepare features: company size, experience, job title, tech stack, etc.
3. **Calls Gemini API with synthetic job descriptions** to generate salary predictions
4. Stores predictions in-notebook only (no model export)

**Outputs**: Prediction results (stored in variables, not persisted)

**Issues**:
- ⚠️ **CRITICAL**: Gemini API key hardcoded
- Data loading duplicated verbatim from `preprocess_job_cluster`
- No actual ML model training (just Gen-AI API calls)
- Predictions not saved to CSV/database for audit trail
- No feature importance analysis
- No cross-validation or test/train split

---

### 2.5 `topdev_evaluate_salary_model.ipynb` (17 code cells)

**Purpose**: Evaluate salary prediction accuracy

**Key Steps**:
1. Load & preprocess (DUPLICATE)
2. Split into train/test sets
3. For each test sample, call Gemini API to predict salary
4. Compare predictions vs. actual salaries
5. Calculate RMSE, MAE metrics

**Outputs**: Accuracy metrics (in-notebook), test predictions

**Issues**:
- ⚠️ **CRITICAL**: Gemini API key hardcoded (different from feature.py!)
- Data loading duplicated again
- No model serialization (can't reproduce predictions later)
- Evaluation metrics not persisted (no audit trail)
- No confidence intervals or error bands
- Test set not shuffled/stratified

---

### 2.6 Duplicated Logic Across Notebooks

**CRITICAL DUPLICATION**: Data loading & preprocessing repeated **4 times**:

```python
# Appears identically in ALL of these:
# - topdev_preprocess_all_in_one.ipynb (cells 1-7)
# - topdev_preprocess_job_cluster.ipynb (cells 1-12)
# - topdev_model_preparation.ipynb (cells 1-7)
# - topdev_evaluate_salary_model.ipynb (cells 1-7)

directory = "csv_backup"
dataframes = []
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path)
        df = df.drop_duplicates()
        dataframes.append(df)
data = pd.concat(dataframes)

# Then identical parsing logic:
for col in data.columns:
    if col not in ["thong_tin_cong_ty", "url", "url_cong_ty", "thoi_gian_hien_tai"]:
        data[col] = data[col].apply(ast.literal_eval)
```

**IMPACT**: 
- 4x computational waste (reprocessing same data)
- 4x opportunity for inconsistency (if one notebook is updated, others drift)
- Maintenance nightmare (bug fix must be applied 4 times)

---

## 3. PYTHON APP DEEP-DIVE

### 3.1 `app.py` (44 lines) — Main Entry Point

**Purpose**: Streamlit app launcher; orchestrates 4 tabs

**Structure**:
```python
st.set_page_config(layout="wide")
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Recommendation", "Q&A", "Feature"])
# Each tab calls a function from dashboard.py, recommendation.py, chatbot.py, feature.py
```

**Issues**:
- No error handling (if a tab crashes, whole app crashes)
- Hardcoded layout; not responsive to screen size
- No session state management across tabs

---

### 3.2 `dashboard.py` (29 lines) — MongoDB Charts Iframe

**Purpose**: Embed MongoDB Charts visualization

**Implementation**: 
```python
def tab_1():
    st.components.v1.html(iframe with hardcoded dashboard_url)
```

**Issues**:
- ⚠️ Dashboard URL hardcoded (non-portable; breaks if URL changes)
- No fallback if MongoDB service down
- No caching strategy

---

### 3.3 `recommendation.py` (155 lines) — Content-Based Recommendation

**Purpose**: Keyword-based job matching with weighted ranking

**Algorithm**:
1. User inputs keywords (multi-input UI)
2. Filter jobs containing ALL keywords
3. Calculate match score: `Σ(weight_i × matches_i) / sum(weights)`
4. Weights hardcoded for 12 features (job title: 10, company: 5, etc.)
5. Rank by score; display top-N results

**Outputs**: Ranked job table

**Issues**:
- Weights hardcoded; no tuning mechanism
- Duplicated data transformations (also in `feature.py`):
  ```python
  df['quy_mo_cong_ty'] = df['quy_mo_cong_ty'].apply(lambda x: f"Quy mô {x}")
  df['dia_chi'] = df['dia_chi'].apply(extract_city_province)
  # ... 8 more transformations
  ```
- No TF-IDF or semantic similarity (naive string contains)
- Scale grows linearly with dataset size (no indexing)

---

### 3.4 `chatbot.py` (72 lines) — Q&A Bot

**Purpose**: Answer questions about job market data

**Implementation**:
```python
api_key = os.getenv("HUGGINGFACE_API_KEY")  # ✓ Loaded from .env
client = InferenceClient(api_key=api_key)
# For each question, prepend entire CSV as context
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3.2",
    messages=[{"role": "user", "content": base_prompt + user_input}]
)
```

**Issues**:
- ⚠️ **CONTEXT WINDOW RISK**: Sending entire CSV as context (memory inefficient, slow)
- Chat history commented out (feature incomplete)
- No rate limiting (potential API cost spike)
- Model hardcoded to DeepSeek-V3.2 (no fallback)
- No validation that LLM answer is factually grounded in data

---

### 3.5 `feature.py` (241 lines) — Feature Lab (Salary & Advice)

**Purpose**: Interactive feature exploration; salary prediction & interview prep

**Components**:

1. **Job Browser**: Select from dataset, edit job details in form
2. **Salary Predictor**: 
   ```python
   model = genai.GenerativeModel('gemini-2.5-flash')
   # Prompt with 14 job attributes
   response = model.generate_content(prompt)  # Parse LLM output as salary range
   ```
3. **Advice Generator**: Same prompt + candidate description → career advice

**Issues**:
- ⚠️ **CRITICAL**: Gemini API key hardcoded (visible in line 9)
- Duplicated data loading & transformation logic (23 lines identical to `recommendation.py`)
- **Salary prediction fragile**: Parsing LLM text output as numeric range (regex brittle)
- PDF generation code commented out (incomplete feature)
- No validation that predicted salary is reasonable (could hallucinate)
- Hardcoded to `gemini-2.5-flash` model; no versioning strategy

---

### 3.6 `test.py` (minimal file)

**Status**: Appears to be a leftover testing stub; minimal content

---

## 4. SECURITY & OPERATIONAL RISKS

### CRITICAL ISSUES (Production-Breaking)

| Issue | Severity | Files | Impact |
|-------|----------|-------|--------|
| **Gemini API key hardcoded** | 🔴 CRITICAL | `feature.py` (line 9), notebooks | Key exposed in public repo; compromised |
| **MongoDB URI + credentials hardcoded** | 🔴 CRITICAL | Preprocessing notebooks (4 files) | Database access compromised |
| **GitHub credentials hardcoded** | 🔴 CRITICAL | Crawler notebook | Account hijacked; scraping blocked |
| **HuggingFace API key hardcoded** | 🔴 CRITICAL | `topdev_model_preparation.ipynb` | Rate-limited; cost exposure |
| **Data loading logic duplicated 4x** | 🔴 CRITICAL | All notebooks | Maintenance burden; inconsistency |
| **No error handling (app crashes)** | 🔴 CRITICAL | All Python files | User-facing failures |

### HIGH ISSUES (Data/Availability)

| Issue | Severity | Impact |
|-------|----------|--------|
| Entire CSV context sent to LLM | 🟠 HIGH | Latency, cost, context limit exceeded |
| No data validation pipeline | 🟠 HIGH | Garbage-in-garbage-out |
| Salary parsing via LLM text (regex brittle) | 🟠 HIGH | Prediction failures, hallucination |
| Notebook logic not reproducible | 🟠 HIGH | Can't retrain if data changes |
| No logging or monitoring | 🟠 HIGH | Silent failures in production |

### MEDIUM ISSUES (Operational)

- No API rate limiting (could spike costs unexpectedly)
- No caching for expensive API calls
- MongoDB connection pooling missing (bottleneck at scale)
- Selenium crawler not robust to UI changes
- Job clustering rules hardcoded (not maintainable)

---

## 5. ACTIONABLE IMPROVEMENTS (Prioritized by Impact)

### 🎯 TIER 1: CRITICAL (Do First - Blocks Production)

#### 1. **Secrets Management - Eliminate Hardcoded Keys**
   - **Current**: API keys visible in code, notebooks, git history
   - **Action**:
     - Migrate all API keys to `.env` file (model: `chatbot.py` already does this correctly)
     - Add `.env` to `.gitignore`; commit `.env.example` only
     - Use `python-dotenv` consistently across all modules
     - Rotate all exposed keys immediately
     - Add pre-commit hook to catch secrets
   - **Files to Update**: `feature.py` (line 9), all 4 preprocessing notebooks, crawler notebook
   - **Priority**: **Week 1** (before any deployment)

#### 2. **Data Pipeline Consolidation - DRY Principle**
   - **Current**: Data loading duplicated in 4 notebooks (copy-paste code smell)
   - **Action**:
     - Extract common preprocessing into `data_loader.py`:
       ```python
       # data_loader.py
       def load_and_preprocess():
           """Single source of truth for data pipeline"""
           directory = "csv_backup"
           dataframes = [pd.read_csv(f) for f in glob(f"{directory}/*.csv")]
           data = pd.concat(dataframes).drop_duplicates()
           return parse_and_normalize(data)
       ```
     - Update all notebooks to import & call `load_and_preprocess()`
     - Version this module in git; make it reusable
   - **Benefit**: Single point of maintenance; consistency guarantee
   - **Priority**: **Week 1-2**

#### 3. **Notebook-to-Module Transition**
   - **Current**: Critical logic in Jupyter cells (non-reproducible, hard to test)
   - **Action**:
     - Convert `topdev_preprocess_job_cluster.ipynb` → `preprocess.py` module
     - Convert `topdev_model_preparation.ipynb` → `salary_model.py` module
     - Keep notebooks for **exploration only** (marked as `_exploratory.ipynb`)
     - Create CLI entry point: `python preprocess.py --input csv_backup/ --output processed_data.csv`
   - **Benefit**: Reproducible pipeline; CI/CD ready
   - **Priority**: **Week 2-3**

#### 4. **Add Error Handling & Logging**
   - **Current**: No try-catch; app crashes silently
   - **Action**:
     ```python
     # app.py
     import logging
     logging.basicConfig(level=logging.INFO)
     logger = logging.getLogger(__name__)
     
     try:
         tab_1()
     except Exception as e:
         logger.error(f"Tab 1 failed: {e}")
         st.error("Dashboard unavailable. Please refresh.")
     ```
   - Apply to all 4 tab functions + API calls
   - **Priority**: **Week 1**

---

### 🎯 TIER 2: HIGH (Production-Ready)

#### 5. **Chatbot Context Optimization - Move from Full CSV to RAG**
   - **Current**: Sends entire CSV to LLM (inefficient, slow, expensive)
   - **Action**:
     - Install vector DB: `pip install chromadb` or Pinecone
     - Split `processed_data.csv` into chunks (one row per chunk)
     - Embed chunks using sentence-transformers
     - For each user query:
       - Retrieve top-3 relevant jobs (semantic search)
       - Send only relevant jobs + query to LLM
     ```python
     # chatbot.py (revised)
     from chromadb import Client
     
     def get_relevant_context(query, top_k=3):
         results = chromadb_client.query(query, top_k=top_k)
         return format_results_as_text(results)
     
     response = client.chat.completions.create(
         model="deepseek-ai/DeepSeek-V3.2",
         messages=[{"role": "user", "content": get_relevant_context(user_input) + user_input}]
     )
     ```
   - **Benefit**: 5-10x faster, 50% cost reduction, better accuracy
   - **Priority**: **Week 3-4**

#### 6. **Reproducible Model Evaluation**
   - **Current**: Predictions ephemeral (in-memory only); no model artifact
   - **Action**:
     - Save salary predictions + actuals to `predictions.csv`:
       ```python
       results_df = pd.DataFrame({
           'job_id': test_ids,
           'actual_salary': test_salaries,
           'predicted_salary': predictions,
           'model': 'gemini-2.5-flash',
           'timestamp': datetime.now()
       })
       results_df.to_csv('evaluation_results.csv', append=True)
       ```
     - Calculate metrics: RMSE, MAE, MAPE, R²
     - Create evaluation report: `generate_evaluation_report(results_df)`
   - **Priority**: **Week 2**

#### 7. **Data Validation Schema**
   - **Current**: No schema enforcement; garbage-in-garbage-out
   - **Action**:
     ```python
     # schema.py
     from pydantic import BaseModel
     
     class JobListing(BaseModel):
         ten_cong_viec: str
         muc_luong: List[int]  # [min, max] in USD
         nam_kinh_nghiem: int
         dia_chi: List[str]
         # ... validate all fields
     
     # In preprocess.py
     for row in data.iterrows():
         try:
             JobListing(**row)
         except ValidationError as e:
             logger.warning(f"Invalid row {row.id}: {e}")
     ```
   - **Benefit**: Early error detection; clear data contracts
   - **Priority**: **Week 3**

#### 8. **Recommendation Engine Upgrade - Move to TF-IDF**
   - **Current**: Naive string matching; O(n) time complexity
   - **Action**:
     ```python
     from sklearn.feature_extraction.text import TfidfVectorizer
     from sklearn.metrics.pairwise import cosine_similarity
     
     vectorizer = TfidfVectorizer()
     job_vectors = vectorizer.fit_transform(df['combined_text'])
     
     def recommend(query, top_n=5):
         query_vector = vectorizer.transform([query])
         similarities = cosine_similarity(query_vector, job_vectors)[0]
         return df.iloc[similarities.argsort()[-top_n:][::-1]]
     ```
   - **Benefit**: Semantic similarity; sub-second performance at 10K+ jobs
   - **Priority**: **Week 4**

#### 9. **Salary Prediction - Switch from LLM Text Parsing to Structured Output**
   - **Current**: Parse LLM text output "100 - 150 USD" via regex (brittle)
   - **Action**:
     ```python
     prompt = "Predict salary as JSON: {\"min_salary\": ..., \"max_salary\": ...}"
     response = model.generate_content(prompt)
     result = json.loads(response.text)  # Guaranteed structure
     ```
   - Alternatively: Fine-tune a regression model on historical salary data
   - **Priority**: **Week 3-4**

#### 10. **API Rate Limiting & Caching**
   - **Current**: No rate limiting; uncapped API calls
   - **Action**:
     ```python
     import streamlit as st
     from functools import lru_cache
     
     @st.cache_data(ttl=3600)  # Cache for 1 hour
     def predict_salary(job_desc):
         return model.generate_content(job_desc).text
     
     # Also add request throttling:
     from ratelimit import limits, sleep_and_retry
     
     @sleep_and_retry
     @limits(calls=100, period=3600)  # 100 calls/hour
     def call_gemini_api(...):
         ...
     ```
   - **Benefit**: Cost control; faster UX
   - **Priority**: **Week 2**

---

### 🎯 TIER 3: MEDIUM (Analytics & Monitoring)

#### 11. **Automated Data Pipeline (CI/CD)**
   - **Current**: Manual notebook execution; no schedule
   - **Action**:
     - Create GitHub Actions workflow:
       ```yaml
       # .github/workflows/refresh_data.yml
       name: Refresh Job Data
       on:
         schedule:
           - cron: '0 9 * * MON'  # Every Monday 9 AM
       jobs:
         crawl:
           runs-on: ubuntu-latest
           steps:
             - uses: actions/checkout@v2
             - run: pip install -r requirements.txt
             - run: python crawler.py --output csv_backup/
             - run: python preprocess.py --output processed_data.csv
             - run: git add processed_data.csv && git commit -m "Auto: refresh data"
             - run: git push
       ```
   - **Benefit**: Weekly fresh data; no manual intervention
   - **Priority**: **Week 4-5**

#### 12. **Experiment Tracking for Salary Model**
   - **Current**: Predictions not tracked; no A/B testing capability
   - **Action**:
     - Use MLflow or Weights & Biases:
       ```python
       import mlflow
       
       mlflow.start_run()
       mlflow.log_param("model", "gemini-2.5-flash")
       mlflow.log_metric("rmse", rmse_value)
       mlflow.log_artifact("predictions.csv")
       mlflow.end_run()
       ```
   - Track model versions, hyperparameters, metrics
   - **Priority**: **Week 5**

#### 13. **Business Metrics Dashboard**
   - **Current**: Only data exploration; no KPIs
   - **Action**:
     - Create metrics dashboard (separate Streamlit page):
       - # jobs crawled (trend over time)
       - Salary distribution by seniority level
       - Top 10 most in-demand skills
       - Average salary by skill, location, company size
       - User engagement (# searches, recommendations clicked)
     - Connect to MongoDB for historical trending
   - **Priority**: **Week 6**

#### 14. **Salary Prediction Model Benchmarking**
   - **Current**: No baseline; Gen-AI model not validated
   - **Action**:
     - Split historical data: train (80%), test (20%)
     - Train 3 models in parallel:
       1. Gemini (current approach)
       2. XGBoost regression on features (title, exp, location, tech stack)
       3. Linear regression baseline
     - Compare RMSE, MAE, inference time
     - Log results to `model_benchmark.csv`
   - **Benefit**: Know if Gen-AI is worth the cost vs. classical ML
   - **Priority**: **Week 5-6**

#### 15. **Documentation & Governance**
   - **Current**: Minimal docs; unclear data lineage
   - **Action**:
     - Create `ARCHITECTURE.md`:
       - Data flow diagram (Mermaid)
       - API contracts (request/response schemas)
       - Config management (where keys are loaded)
       - Troubleshooting guide
     - Create `RUNBOOK.md`:
       - How to refresh data
       - How to deploy to production
       - Common errors & fixes
     - Add data dictionary: `DATA_DICTIONARY.md` (column definitions, units, valid ranges)
   - **Priority**: **Week 3** (parallel with code work)

---

## 6. SECURITY & BUSINESS ALIGNMENT IMPROVEMENTS

### Data Engineering (Tier 1)
1. ✅ Consolidate preprocessing logic into reusable module
2. ✅ Add data validation schema (Pydantic)
3. ✅ Version all data artifacts in git (or DVC)
4. ✅ Implement data lineage tracking

### ML/Analytics (Tier 1)
5. ✅ Reproducible model evaluation (save predictions, metrics)
6. ✅ Benchmark salary model vs. statistical baseline
7. ✅ Move from LLM text parsing to structured JSON output
8. ✅ Experiment tracking (MLflow/W&B)

### Product/UX (Tier 2)
9. ✅ Add business KPI dashboard (market trends, user engagement)
10. ✅ Implement RAG for chatbot (better relevance, lower cost)
11. ✅ TF-IDF recommendation engine (faster, more scalable)
12. ✅ Salary prediction confidence intervals (don't just show point estimate)

### MLOps/DevOps (Tier 1)
13. ✅ Secrets management (env variables, not hardcoded keys)
14. ✅ Error handling + logging across all components
15. ✅ Automated data pipeline (GitHub Actions)
16. ✅ Model versioning & artifact management

### Business Impact
- **Governance**: Clear data contracts, audit trails, model explainability
- **Scalability**: Move from notebooks to production code; handle 100K+ jobs
- **Cost Control**: Cache expensive LLM calls; use classical ML where appropriate
- **User Trust**: Show confidence intervals, data sources, prediction reasoning

---

## 7. SUGGESTED DELIVERABLE MARKDOWN OUTLINE

Create a **`OPERATIONS.md`** file in the repo root:

```markdown
# Job Market Analytics - Operations Guide

## 📋 Quick Reference

### Project Structure
- `/csv_backup/` — Historical raw data snapshots
- `processed_data.csv` — Clean dataset (updated weekly)
- `notebooks/` — Exploration & analysis (archived)
- `src/` — Production code modules
  - `data_loader.py` — Data pipeline
  - `preprocess.py` — Normalization, clustering
  - `salary_model.py` — Prediction logic
  - `app.py` — Streamlit UI
- `tests/` — Unit & integration tests
- `.github/workflows/` — CI/CD pipelines

### Configuration
- Copy `.env.example` → `.env`
- Required variables:
  - `GOOGLE_API_KEY` (Gemini)
  - `HUGGINGFACE_API_KEY` (LLM)
  - `MONGODB_URI` (Atlas connection)
- Never commit `.env`

### Running the Pipeline
```bash
# 1. Crawl new data
python src/crawler.py --output csv_backup/topdev_$(date +%Y%m%d).csv

# 2. Preprocess & validate
python src/preprocess.py --input csv_backup/ --output processed_data.csv

# 3. Evaluate salary model
python src/salary_model.py --evaluate --input processed_data.csv

# 4. Deploy app
streamlit run app.py
```

### Monitoring & Troubleshooting
- **Crawler fails**: Check GitHub auth, TopDev URL, Selenium driver
- **Preprocessing slow**: Check file count in csv_backup/; consider archiving old files
- **API rate limit**: Check logs; implement backoff strategy
- **Salary predictions invalid**: Validate LLM output schema; add fallback to statistical model

### KPIs to Track
- Data freshness (how old is processed_data.csv?)
- Salary prediction accuracy (RMSE vs. test set)
- User engagement (searches/day, recommendations clicked)
- API costs (Gemini + HuggingFace)

### Deployment Checklist
- [ ] All secrets in .env (not in code)
- [ ] Error handling tested
- [ ] Data validation passing
- [ ] Model evaluation report generated
- [ ] Documentation updated
- [ ] Load-tested with 100K jobs
```

---

## SUMMARY TABLE: Impact vs. Effort

| Recommendation | Impact | Effort | Timeline | Priority |
|----------------|--------|--------|----------|----------|
| 1. Secrets Management | 🔴 High (production blocker) | Low (1 day) | Week 1 | 🔴 |
| 2. DRY Consolidation | 🟠 High (maintainability) | Low (2 days) | Week 1-2 | 🔴 |
| 3. Notebook → Module | 🟠 High (reproducibility) | Medium (3 days) | Week 2-3 | 🔴 |
| 4. Error Handling | 🟠 High (reliability) | Low (1 day) | Week 1 | 🔴 |
| 5. RAG for Chatbot | 🟢 Medium (UX + cost) | High (5 days) | Week 3-4 | 🟡 |
| 6. Model Reproducibility | 🟢 Medium (governance) | Low (2 days) | Week 2 | 🟡 |
| 7. Data Validation | 🟢 Medium (data quality) | Medium (3 days) | Week 3 | 🟡 |
| 8. TF-IDF Recommendation | �� Medium (performance) | Medium (3 days) | Week 4 | 🟡 |
| 9. Structured LLM Output | 🟢 Medium (reliability) | Low (1 day) | Week 3 | 🟡 |
| 10. Rate Limiting | 🟢 Medium (cost control) | Low (1 day) | Week 2 | 🟡 |
| 11. Automated Pipeline | 🟢 Low (convenience) | High (5 days) | Week 4-5 | 🟢 |
| 12. Experiment Tracking | 🟢 Low (analytics) | Medium (3 days) | Week 5 | 🟢 |
| 13. Business Metrics | 🟢 Low (analytics) | Medium (4 days) | Week 6 | 🟢 |
| 14. Model Benchmarking | 🟢 Low (validation) | Low (2 days) | Week 5-6 | 🟢 |
| 15. Documentation | 🟠 Medium (communication) | Low (2 days) | Week 3 (parallel) | 🟡 |

---

## FINAL ASSESSMENT

### Strengths
✅ **End-to-end pipeline** from data crawl → prediction → UI  
✅ **Multi-modal AI integration** (classical ML + Gen-AI + LLM)  
✅ **Real-world problem** (job market analytics) with clear business value  
✅ **Team collaboration** (6-person capstone; modular code)  

### Weaknesses
❌ **Production-unfriendly**:  
- Hardcoded secrets (CRITICAL)  
- Notebook-only logic (non-reproducible)  
- Duplicated code (4x data loading)  
- No error handling (crashes)  

❌ **Analytics gaps**:  
- No model benchmarking  
- No A/B testing framework  
- No business KPI tracking  
- Salary model purely Gen-AI (not validated vs. statistical baseline)  

❌ **Scalability issues**:  
- Full CSV sent to LLM (scales linearly with data)  
- Naive string matching for recommendations  
- No data versioning or experiment tracking  

### Actionable Path to Production
1. **Week 1**: Eliminate secrets, add error handling, consolidate data loading
2. **Week 2-3**: Convert critical notebooks to modules; add evaluation tracking
3. **Week 4**: Implement RAG for chatbot; TF-IDF recommendations
4. **Week 5+**: Automate pipeline; experiment tracking; KPI dashboard

### Alignment with Data Scientist + Business Analyst Roles
- ✅ **Data exploration & cleaning** (strong; notebooks show good EDA)
- ✅ **Feature engineering** (present; job title translation, clustering)
- ❌ **Model evaluation & governance** (weak; no proper evaluation framework)
- ❌ **Business metrics & communication** (weak; no KPI dashboard or storytelling)
- ❌ **Production readiness** (weak; secrets exposed, no CI/CD)
- ⚠️ **Experimentation** (emerging; recommendations weighting but no A/B testing)

**Score**: 5.5/10 as capstone; 3/10 as production-ready

