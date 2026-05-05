# 🎯 Automated Resume Screening Tool

> AI-powered ATS simulation using Python · TF-IDF · Cosine Similarity · Streamlit

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.1+-orange?logo=scikit-learn)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🏢 Problem Statement

Every job posting receives **200–500+ applications**. HR teams spend hours manually screening resumes — most of which don't match the role. This wastes 60–70% of recruiter time.

**This tool solves it** by automatically comparing resumes against job descriptions using NLP and machine learning, scoring each candidate, and generating a ranked shortlist.

---

## 💡 What This Tool Does

```
Resume Upload → Text Extraction → Cleaning → TF-IDF Vectorization
      ↓
Skill Keyword Matching + Cosine Similarity + Experience Scoring
      ↓
Composite Score (0-100) → Ranked Table → Shortlist/Reject Decision
      ↓
CSV Report + JSON Export + Streamlit Dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.9+ |
| NLP / ML | Scikit-learn (TF-IDF, Cosine Similarity) |
| Text Processing | NLTK, Regex |
| PDF Extraction | pdfplumber |
| DOCX Extraction | python-docx |
| Data | Pandas, NumPy |
| Dashboard | Streamlit + Plotly |
| Reports | CSV, JSON |

---

## 📁 Folder Structure

```
Automated-Resume-Screening-Tool/
│
├── resumes/                  ← Sample resume files (.txt/.pdf/.docx)
│   ├── resume_arjun_sharma.txt
│   ├── resume_priya_nair.txt
│   ├── resume_sneha_reddy.txt
│   ├── resume_vikram_patel.txt
│   └── resume_rahul_gupta.txt
│
├── data/
│   └── job_descriptions.json ← 3 job descriptions with required skills
│
├── src/                      ← Core Python modules
│   ├── text_extractor.py     ← PDF/DOCX/TXT text extraction
│   ├── text_cleaner.py       ← NLP preprocessing pipeline
│   ├── scorer.py             ← TF-IDF + cosine similarity scoring
│   └── report_generator.py  ← CSV/JSON report generation
│
├── outputs/                  ← Generated reports (auto-created)
├── images/                   ← Screenshots for documentation
├── docs/                     ← Additional documentation
│
├── main.py                   ← CLI pipeline runner
├── dashboard.py              ← Streamlit web dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/Automated-Resume-Screening-Tool.git
cd Automated-Resume-Screening-Tool
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run CLI tool
```bash
python main.py
```

### 5. Run Dashboard
```bash
streamlit run dashboard.py
```
Then open → `http://localhost:8501`

---

## 📊 Sample Output

### Terminal Output
```
====================================================================
  RESUME SCREENING RESULTS  |  Job: Python Developer / Data Analyst
====================================================================
RANK  CANDIDATE               SCORE   SKILL %   TF-IDF  DECISION
--------------------------------------------------------------------
1     Sneha Reddy              78.4    83.3%      71.2%  ✅ Strongly Shortlisted
2     Arjun Sharma             72.1    75.0%      65.8%  ✅ Shortlisted
3     Priya Nair               61.3    58.3%      54.9%  ✅ Shortlisted
4     Vikram Patel             44.7    33.3%      38.2%  ⚠️  Maybe (Review Manually)
5     Rahul Gupta               8.3     0.0%       7.1%  ❌ Rejected
====================================================================
SUMMARY: 5 resumes processed
✅ Shortlisted : 3
⚠️ Manual Review: 1
❌ Rejected    : 1
====================================================================
```

### CSV Output (outputs/Python_Developer_*.csv)

| Rank | Candidate | Score | Skill % | Decision |
|------|-----------|-------|---------|----------|
| 1 | Sneha Reddy | 78.4 | 83.3% | Strongly Shortlisted |
| 2 | Arjun Sharma | 72.1 | 75.0% | Shortlisted |

---

## 🔢 Scoring Formula

```
Final Score = (TF-IDF Cosine Similarity × 0.50)
            + (Skill Keyword Match %   × 0.40)
            + (Experience Score        × 0.10)

Shortlisted        → Score ≥ 75
Shortlisted        → Score ≥ 55
Maybe              → Score ≥ 35
Rejected           → Score < 35
```

---

## 🎓 Learning Outcomes

After building this project, you can explain:
- How ATS systems work in HR tech
- TF-IDF vectorization and cosine similarity
- NLP preprocessing (tokenization, stopword removal, stemming)
- Text extraction from PDF and DOCX files
- Building Streamlit dashboards with Plotly charts
- Modular Python project structure
- GitHub documentation best practices

---

## 💼 Interview Questions This Project Covers

1. Explain your project and its real-world use case
2. What is TF-IDF and how does it measure relevance?
3. How does cosine similarity work?
4. How did you extract text from PDFs?
5. How is the scoring algorithm designed?
6. What is NLP preprocessing and why is it needed?
7. How would you improve this in production?
8. What Python libraries did you use and why?
9. How did you handle multiple file formats?
10. How would you deploy this as a web application?

---

## 🗓️ Build Timeline

| Day | Task |
|-----|------|
| Day 1 | Setup, folder structure, dependencies |
| Day 2 | Resume text extraction (TXT/PDF/DOCX) |
| Day 3 | Job description matching + TF-IDF |
| Day 4 | Scoring algorithm + ranking |
| Day 5 | Report generation + CSV output |
| Day 6 | Streamlit dashboard |
| Day 7 | GitHub documentation + README |

---

## 👤 Author

**[Your Name]** — Python Developer | Data Analyst | AI Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/seshu-8)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/seshu-babu-konijeti-74968b2b9?utm_source=share_via&utm_content=profile&utm_medium=member_android)

---

## 📄 License

MIT License — free to use, modify, and distribute.
