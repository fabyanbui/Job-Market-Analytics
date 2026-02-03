# Job Market Analytics & Intelligent Application

## Project Overview
**Role**: Full Stack Data Science Developer (Team of 6)
**Duration**: University Capstone Project
**Technologies**: Python, Selenium, Pandas, Streamlit, MongoDB, Google Gemini API, HuggingFace API (Mistral), LangChain.

---

## 🌟 STAR Experience Summary

### **Situation**
The IT job market in Vietnam is dynamic and often opaque. Job seekers struggle to find relevant opportunities, understand valid salary expectations for their skill levels, and tailor their CVs to specific requirements. Existing platforms often lack personalized insights or interactive data visualizations.

### **Task**
The objective was to build an end-to-end **Intelligent Data Analytics Application** that:
1.  **Aggregates** real-time job data from major portals (TopDev).
2.  **Analyzes** trends in salaries, skills, and company attributes.
3.  **Provides** value-added services: Personalized Job Recommendations, AI-powered Salary Prediction, and Resume Advice.

### **Action**
I (and the team) implemented a full data pipeline and application stack:

#### 1. Data Acquisition (Web Crawling)
*   **Tool**: `Selenium`
*   **Implementation**: Developed robust scripts to crawl TopDev. handled dynamic content loading (infinite scrolling), authentication (GitHub login automation), and anti-bot measures.
*   **Scale**: Collected detailed data points (Salary, Experience, Tech Stack, Company Info) for thousands of job postings.

#### 2. Data Engineering & Preprocessing
*   **Tool**: `Pandas`, `NumPy`, `Regex`, `Deep Translator`
*   **Cleaning**: Implemented complex logic to parse "Thương lượng" (Negotiable) salaries and normalize mixed currencies (VND/USD) into a unified USD scale.
*   **Feature Engineering**: 
    *   Parsed stringified attributes (Skills, Locations) back into usable lists.
    *   **Automated Translation**: Used `deep_translator` to normalize Vietnamese job titles to English for consistent aggregation.
    *   **Rule-based Clustering**: Categorized thousands of unique job titles into standard groups (e.g., "Software/Web/Mobile", "Data & AI", "DevOps") for better analytics.

#### 3. Application Development (Streamlit)
Built a multi-module **Streamlit** web application with four core features:
*   **Dashboard**: Embedded **MongoDB Charts** via iframe for interactive visualization of industry trends (Salary by Experience, Top Skills).
*   **Recommendation Engine**: Built a **Content-Based Filtering System**. Implemented a weighted algorithms allowing users to input keywords (Skills, Location, Salary) and receive ranked job matches based on similarity scores.
*   **AI Integration (GenAI)**:
    *   **Salary Prediction**: Integrated **Google Gemini Pro** to analyze the full context of a job description (requirements, benefits, scale) and predict a realistic salary range.
    *   **Chatbot**: Implemented a Q&A bot using **HuggingFace (Mistral-8x7B)** and **LangChain** to allow users to ask natural language questions about the dataset.

### **Result**
*   **Deliverable**: A fully functional web application deployed on Streamlit Cloud.
*   **Impact**: successfully automated the analysis of thousands of jobs, providing clear salary benchmarks.
*   **Innovation**: Combined traditional analytics (Charts) with Generative AI (Salary Prediction) and traditional Machine Learning (Recommendation Systems) in a single user-friendly interface.

---

## 📂 Technical Deep Dive

### 1. Project Structure
```text
├── app.py                      # Main Streamlit entry point
├── chatbot.py                  # LLM Chatbot implementation (Mistral)
├── recommendation.py           # Content-based recommendation logic
├── feature.py                  # Gemini integrations (Salary & CV)
├── topdev_crawler_save_time.ipynb  # Selenium Crawler logic
└── topdev_preprocess_job_cluster.ipynb # Data cleaning pipeline
```

### 2. Key Challenges & Solutions
*   **Dirty Data**: Salary fields were highly inconsistent (ranges, fixed numbers, text).
    *   *Solution*: Wrote rigorous Regex parsers to extract min/max values and standardized them to a monthly USD average.
*   **Job Title Ambiguity**: "Senior Dev", "Sr. Developer", "Chuyên viên lập trình" refer to the same role.
    *   *Solution*: Applied a translation layer followed by keyword-based clustering (e.g., if title contains "React" or "Java" → "Software Development").
*   **LLM Latency**: AI calls can be slow.
    *   *Solution*: Used Streamlit's session state to cache inputs and results, preventing unnecessary API calls during UI interactions.

### 3. Future Improvements
*   **Vector Database**: Move from CSV-based context to a Vector DB (ChromaDB/Pinecone) for RAG (Retrieval Augmented Generation) to improve Chatbot accuracy.
*   **Automated Pipeline**: Schedule the crawler to run weekly using GitHub Actions or Airflow to keep data fresh.
