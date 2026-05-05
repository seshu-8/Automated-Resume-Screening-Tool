# 🎤 Interview Preparation — Automated Resume Screening Tool

---

## Q1. Explain your project.

**Answer (for any interviewer):**

"I built an Automated Resume Screening Tool — a Python-based ATS simulation that automatically scores and ranks resumes against a job description.

The system extracts text from PDF, DOCX, or TXT files, cleans the text using NLP preprocessing, then scores each resume using two methods: TF-IDF cosine similarity for semantic matching, and direct keyword matching for required skills. These scores are combined into a weighted composite score (0–100). Candidates above the threshold are shortlisted, others are rejected.

I also built a Streamlit dashboard with Plotly charts for visual analysis, and the system exports ranked results as CSV and JSON reports.

This project demonstrates Python, NLP, machine learning, data processing, and UI development — all relevant to Data Analyst, Python Developer, and HR Tech roles."

---

## Q2. What is TF-IDF and how does it work?

**Simple:**
TF-IDF stands for Term Frequency–Inverse Document Frequency. It's a method to measure how important a word is to a document. Words that appear often in one document but rarely in others get a high score — this helps identify relevant, unique terms.

**Technical:**
- TF (Term Frequency) = (count of word in document) / (total words in document)
- IDF (Inverse Document Frequency) = log(total documents / documents containing the word)
- TF-IDF = TF × IDF
- In my project: I vectorize both the resume and job description using TF-IDF, then measure their cosine similarity to determine how semantically similar they are.

---

## Q3. How does cosine similarity work?

**Simple:**
Cosine similarity measures the angle between two vectors. If two documents are very similar, their vectors point in the same direction (angle ≈ 0°, cosine ≈ 1.0). If they're completely different, the angle is 90° (cosine = 0).

**Technical:**
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```
After TF-IDF vectorization, each resume and job description is a high-dimensional vector. I use `sklearn.metrics.pairwise.cosine_similarity()` to compute the similarity score, which I multiply by 100 to get a percentage.

---

## Q4. How did you extract text from PDF files?

I used the `pdfplumber` library, which extracts text page-by-page from PDF files. For DOCX files, I used `python-docx` which reads paragraph-by-paragraph. For .txt files, I use Python's built-in `open()`. The `text_extractor.py` module handles all three formats with a single `extract_text(filepath)` function.

---

## Q5. Explain your scoring algorithm.

My scoring uses three components:
1. **TF-IDF Cosine Similarity (50%)** — semantic match between resume and JD
2. **Skill Keyword Match (40%)** — how many required skills appear in the resume (using regex word boundaries)
3. **Experience Score (10%)** — heuristic score based on years of experience mentioned

Final Score = (TF-IDF × 0.5) + (Skill Match % × 0.4) + (Experience × 0.1)

Thresholds: ≥75 = Strongly Shortlisted, ≥55 = Shortlisted, ≥35 = Maybe, <35 = Rejected.

---

## Q6. What is NLP preprocessing and why did you need it?

Raw resume text contains noise: emails, phone numbers, punctuation, stopwords (like "the", "and"), and varying cases. NLP preprocessing removes this noise so the TF-IDF model focuses on meaningful words.

My pipeline in `text_cleaner.py`:
1. Lowercase the text
2. Remove URLs, emails, phone numbers
3. Remove special characters (regex)
4. Tokenize (split into words)
5. Remove stopwords (NLTK)
6. Apply Porter Stemming (reduces words to root form)

---

## Q7. How would you improve this in production?

1. Use **BERT embeddings** instead of TF-IDF for deeper semantic understanding
2. Add **named entity recognition** (NER) to extract education, experience, and skills automatically
3. Use a **proper database** (PostgreSQL) to store candidates and job openings
4. Add **authentication and user roles** (HR manager, recruiter)
5. Deploy on **AWS/GCP** with a FastAPI backend
6. Add **feedback loop** — HR can approve/reject and the model learns over time

---

## Q8. What Python libraries did you use and why?

| Library | Why |
|---------|-----|
| scikit-learn | TF-IDF vectorizer and cosine similarity |
| pdfplumber | Reliable PDF text extraction |
| python-docx | DOCX file reading |
| NLTK | Stopwords, tokenization, stemming |
| Pandas | DataFrame for ranking and reports |
| Streamlit | Quick dashboard without frontend code |
| Plotly | Interactive, professional charts |
| Regex (re) | Pattern matching for skills, emails, phones |

---

## Q9. How did you handle multiple resume file formats?

I wrote a `text_extractor.py` module with a master `extract_text(filepath)` function. It reads the file extension and routes to the right extractor: `.txt` → built-in open, `.pdf` → pdfplumber, `.docx` → python-docx. This makes the system extensible — I can add support for `.rtf` or `.odt` by adding one function.

---

## Q10. How would you deploy this as a web application?

1. Keep the Streamlit dashboard as the frontend
2. Containerize with **Docker**: `docker build -t resume-screener .`
3. Deploy to **Streamlit Cloud** (free, GitHub integration, 1-click deploy)
4. Or deploy backend as **FastAPI** on **AWS EC2/Heroku** with the Streamlit frontend pointing to the API
5. Store resumes in **AWS S3**, results in **PostgreSQL RDS**

For this project's demo, I use Streamlit's built-in server locally with `streamlit run dashboard.py`.

---

## 🏆 One-Line Project Pitch

"I built a Python tool that uses TF-IDF and cosine similarity to automatically rank and shortlist resumes against job descriptions — complete with a Streamlit dashboard and CSV report export."
