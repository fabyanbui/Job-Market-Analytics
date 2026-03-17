# Job Market Analytics - Improvements Checklist

Use this checklist to track implementation of the 15 recommended improvements.

---

## 🔴 TIER 1: CRITICAL (Week 1) — Do These First

### 1. Secrets Management
- [ ] Identify all hardcoded API keys:
  - [ ] `feature.py:9` → Gemini key
  - [ ] `topdev_model_preparation.ipynb` → Gemini + HuggingFace keys
  - [ ] `topdev_evaluate_salary_model.ipynb` → Gemini key
  - [ ] `topdev_preprocess_all_in_one.ipynb` → MongoDB URI
  - [ ] `topdev_preprocess_job_cluster.ipynb` → MongoDB URI
  - [ ] `topdev_crawler_save_time.ipynb` → GitHub email + password
- [ ] Create/update `.env.example` with all required variables
- [ ] Modify all files to load from `os.getenv()` or `python-dotenv`
- [ ] Verify `.env` in `.gitignore`
- [ ] Rotate all exposed API keys (create new ones in respective dashboards)
- [ ] Purge secrets from git history: `git filter-repo --invert-paths --path .env`
- [ ] Create `.env` from `.env.example` for local testing

**Reference**: `chatbot.py` is the **correct model** — study how it loads `HUGGINGFACE_API_KEY`

---

### 2. Data Loading Consolidation (DRY Principle)
- [ ] Create `src/data_loader.py`:
  ```python
  def load_and_preprocess(csv_dir="csv_backup/"):
      """Single source of truth for data loading"""
      # Implementation: consolidate 40+ lines from all 4 notebooks
  ```
- [ ] Update all notebooks to import + call `load_and_preprocess()`:
  - [ ] `topdev_preprocess_all_in_one.ipynb`
  - [ ] `topdev_preprocess_job_cluster.ipynb`
  - [ ] `topdev_model_preparation.ipynb`
  - [ ] `topdev_evaluate_salary_model.ipynb`
- [ ] Verify all notebooks produce identical data output
- [ ] Document function signature + return schema in docstring

---

### 3. Error Handling & Logging
- [ ] Add logging to `app.py`:
  - [ ] Configure logger: `logging.basicConfig(level=logging.INFO)`
  - [ ] Wrap each tab function in try-except
  - [ ] Log errors; display user-friendly message: `st.error("Feature unavailable")`
- [ ] Add error handling to `recommendation.py`:
  - [ ] Handle empty CSV load
  - [ ] Handle invalid keyword input
- [ ] Add error handling to `chatbot.py`:
  - [ ] Handle HuggingFace API timeout
  - [ ] Handle malformed response
- [ ] Add error handling to `feature.py`:
  - [ ] Handle Gemini API rate limit
  - [ ] Handle invalid row selection
- [ ] Add error handling to `dashboard.py`:
  - [ ] Handle MongoDB Charts URL not accessible

---

### 4. Model Reproducibility — Save Predictions
- [ ] Create `evaluation_results.csv` schema:
  ```
  job_id, actual_salary_min, actual_salary_max, predicted_salary_min, predicted_salary_max, model, timestamp, rmse, mae
  ```
- [ ] Modify `topdev_evaluate_salary_model.ipynb` to append results to CSV
- [ ] Add metadata: model version, data snapshot timestamp, split info
- [ ] Create function `generate_evaluation_report()` in `src/evaluation.py`
- [ ] Generate & display metrics: RMSE, MAE, MAPE, R²

---

## 🟡 TIER 2: HIGH (Weeks 2-4) — Production Essentials

### 5. Reproducible Model Evaluation
- [ ] Convert `topdev_evaluate_salary_model.ipynb` to `src/salary_model.py` module
- [ ] Implement proper train/test split:
  ```python
  from sklearn.model_selection import train_test_split
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
  ```
- [ ] Add stratified splitting (by company size, experience level)
- [ ] Persist predictions + metrics to `evaluation_results.csv`
- [ ] Calculate confidence intervals for salary predictions
- [ ] Create `create_evaluation_report()` function

---

### 6. Data Validation Schema
- [ ] Create `src/schema.py` with Pydantic models:
  ```python
  class JobListing(BaseModel):
      ten_cong_viec: str
      muc_luong: List[int]  # [min, max]
      nam_kinh_nghiem: int
      dia_chi: List[str]
      # ... more fields
  ```
- [ ] Integrate into `data_loader.py`:
  ```python
  for row in data.iterrows():
      try:
          JobListing(**row)
      except ValidationError as e:
          logger.warning(f"Invalid row {row.id}: {e}")
  ```
- [ ] Log validation errors for review

---

### 7. Chatbot Context Optimization (RAG)
- [ ] Install ChromaDB or Pinecone: `pip install chromadb`
- [ ] Create `src/vector_store.py`:
  ```python
  import chromadb
  client = chromadb.Client()
  collection = client.create_collection(name="jobs")
  # Embed each job as a chunk
  ```
- [ ] Modify `chatbot.py`:
  - [ ] Remove full CSV context
  - [ ] For each query, retrieve top-3 relevant jobs (semantic search)
  - [ ] Send only relevant jobs + query to LLM
- [ ] Measure improvement: latency, cost, user satisfaction

---

### 8. Recommendation Engine Upgrade (TF-IDF)
- [ ] Create `src/recommender.py`:
  ```python
  from sklearn.feature_extraction.text import TfidfVectorizer
  vectorizer = TfidfVectorizer()
  job_vectors = vectorizer.fit_transform(df['combined_features'])
  
  def recommend(query, top_n=5):
      query_vector = vectorizer.transform([query])
      scores = cosine_similarity(query_vector, job_vectors)[0]
      return df.iloc[scores.argsort()[-top_n:][::-1]]
  ```
- [ ] Replace naive string matching in `recommendation.py`
- [ ] Benchmark: latency, relevance (A/B test with users)
- [ ] Document how weights are calculated

---

### 9. Structured LLM Output
- [ ] Update salary prediction prompt in `feature.py`:
  ```python
  prompt = "Predict salary as JSON: {\"min_salary\": ..., \"max_salary\": ...}"
  response = model.generate_content(prompt)
  result = json.loads(response.text)  # Guaranteed structure
  ```
- [ ] Add fallback: if JSON parsing fails, use statistical baseline
- [ ] Validate output range (min < max, reasonable bounds)
- [ ] Add unit test for prompt parsing

---

### 10. Rate Limiting & Caching
- [ ] Install dependencies: `pip install ratelimit streamlit`
- [ ] Add caching to `feature.py`:
  ```python
  @st.cache_data(ttl=3600)  # Cache for 1 hour
  def predict_salary(job_title, company, experience):
      return call_gemini_api(...)
  ```
- [ ] Add rate limiting to all API calls:
  ```python
  from ratelimit import limits, sleep_and_retry
  
  @sleep_and_retry
  @limits(calls=100, period=3600)  # 100 calls/hour
  def call_gemini_api(...):
      ...
  ```
- [ ] Monitor API usage: log each call with cost estimate

---

### 11. Convert Notebooks to Modules
- [ ] Create `src/preprocess.py` from `topdev_preprocess_job_cluster.ipynb`:
  - [ ] `def translate_job_titles()` — Vietnamese to English
  - [ ] `def cluster_jobs()` — Categorize into standard groups
  - [ ] `def extract_salary_range()` — Parse currency, convert to USD
  - [ ] `def normalize_data()` — Clean all fields
  - [ ] Main function: `def run_pipeline(input_dir, output_csv)`
- [ ] Create `src/salary_model.py` from `topdev_model_preparation.ipynb`
- [ ] Create CLI entry point: `python src/preprocess.py --input csv_backup/ --output processed_data.csv`
- [ ] Add argparse for command-line arguments
- [ ] Add progress logging (how many rows processed, time remaining)

---

### 12. Automated Data Pipeline (CI/CD)
- [ ] Create `.github/workflows/refresh_data.yml`:
  ```yaml
  name: Weekly Data Refresh
  on:
    schedule:
      - cron: '0 9 * * MON'  # Every Monday 9 AM
  jobs:
    pipeline:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - run: pip install -r requirements.txt
        - run: python src/crawler.py --output csv_backup/
        - run: python src/preprocess.py --input csv_backup/ --output processed_data.csv
        - run: git add processed_data.csv && git commit -m "Auto: refresh data" || true
        - run: git push
  ```
- [ ] Test workflow locally
- [ ] Verify processed_data.csv is committed weekly

---

## 🟢 TIER 3: MEDIUM (Weeks 5-6) — Advanced Features

### 13. Experiment Tracking (MLflow)
- [ ] Install MLflow: `pip install mlflow`
- [ ] Modify `src/salary_model.py`:
  ```python
  import mlflow
  mlflow.start_run()
  mlflow.log_param("model", "gemini-2.5-flash")
  mlflow.log_metric("rmse", rmse_value)
  mlflow.log_artifact("evaluation_results.csv")
  mlflow.end_run()
  ```
- [ ] Create comparison of multiple models
- [ ] View results: `mlflow ui` → http://localhost:5000

---

### 14. Business KPI Dashboard
- [ ] Create new Streamlit tab: "Analytics"
- [ ] Visualizations:
  - [ ] # jobs crawled (trend over weeks)
  - [ ] Salary distribution (box plot by seniority, location, company size)
  - [ ] Top 10 most in-demand skills
  - [ ] Salary by tech stack (median + quartiles)
  - [ ] Company size distribution
  - [ ] User engagement metrics (searches/day, recommendations clicked)
- [ ] Connect to MongoDB for historical data
- [ ] Add date range picker for temporal analysis

---

### 15. Model Benchmarking
- [ ] Train 3 salary prediction models:
  1. Gemini API (current)
  2. XGBoost on features (company size, experience, tech stack, location)
  3. Linear regression baseline
- [ ] Compare metrics:
  - [ ] RMSE, MAE, MAPE, R²
  - [ ] Inference time (latency)
  - [ ] Cost per prediction
- [ ] Create comparison report: `model_benchmark_report.csv`
- [ ] Document decision: is Gen-AI worth the cost vs. XGBoost?

---

### 16. Documentation (Bonus)
- [ ] Create `ARCHITECTURE.md`:
  - [ ] Data flow diagram (text-based or Mermaid)
  - [ ] Module responsibilities
  - [ ] API contracts (schemas)
  - [ ] Configuration guide
- [ ] Create `RUNBOOK.md`:
  - [ ] How to refresh data
  - [ ] How to deploy to Streamlit Cloud
  - [ ] Common errors & fixes
  - [ ] Troubleshooting guide
- [ ] Create `DATA_DICTIONARY.md`:
  - [ ] Each column definition
  - [ ] Valid ranges/values
  - [ ] Data collection date
- [ ] Create `OPERATIONS.md` (template in ANALYSIS_REPORT.md)

---

## 📊 Progress Tracking

| Item | Status | Due Date | Notes |
|------|--------|----------|-------|
| 1. Secrets Management | ⬜ | Week 1 | CRITICAL |
| 2. Data Loading DRY | ⬜ | Week 1 | CRITICAL |
| 3. Error Handling | ⬜ | Week 1 | CRITICAL |
| 4. Model Reproducibility | ⬜ | Week 1 | CRITICAL |
| 5. Reproducible Evaluation | ⬜ | Week 2 | HIGH |
| 6. Data Validation Schema | ⬜ | Week 2 | HIGH |
| 7. RAG for Chatbot | ⬜ | Week 3 | HIGH |
| 8. TF-IDF Recommendation | ⬜ | Week 3 | HIGH |
| 9. Structured LLM Output | ⬜ | Week 3 | HIGH |
| 10. Rate Limiting | ⬜ | Week 2 | HIGH |
| 11. Notebooks → Modules | ⬜ | Week 2 | HIGH |
| 12. CI/CD Pipeline | ⬜ | Week 4 | MEDIUM |
| 13. Experiment Tracking | ⬜ | Week 5 | MEDIUM |
| 14. KPI Dashboard | ⬜ | Week 5 | MEDIUM |
| 15. Model Benchmarking | ⬜ | Week 5 | MEDIUM |
| 16. Documentation | ⬜ | Week 3 | MEDIUM |

---

## 🎯 Sign-Off

- [ ] All TIER 1 items complete
- [ ] All TIER 2 items complete
- [ ] All TIER 3 items complete
- [ ] Load-tested with 100K+ jobs
- [ ] All documentation updated
- [ ] Ready for production deployment

