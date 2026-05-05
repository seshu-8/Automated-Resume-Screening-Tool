# 📤 GitHub Upload Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com → Click "New repository"
2. Repository name: `Automated-Resume-Screening-Tool`
3. Description: `AI-powered ATS simulation using Python, TF-IDF, Cosine Similarity & Streamlit dashboard`
4. Set to Public
5. Do NOT initialize with README (we have our own)
6. Click "Create repository"

## Step 2: Initialize Git Locally

```bash
cd Automated-Resume-Screening-Tool
git init
git add .
git commit -m "feat: initial project setup with full pipeline"
```

## Step 3: Connect and Push

```bash
git remote add origin https://github.com/YOUR_USERNAME/Automated-Resume-Screening-Tool.git
git branch -M main
git push -u origin main
```

## Step 4: Day-wise Commit Plan

| Day | Files to Commit | Commit Message |
|-----|----------------|----------------|
| Day 1 | requirements.txt, folder structure | `chore: project setup and dependencies` |
| Day 2 | src/text_extractor.py, resumes/ | `feat: add PDF/DOCX/TXT text extraction` |
| Day 3 | src/text_cleaner.py, data/ | `feat: NLP text cleaning and JD loading` |
| Day 4 | src/scorer.py | `feat: TF-IDF scoring and cosine similarity` |
| Day 5 | src/report_generator.py, outputs/ | `feat: CSV and JSON report generation` |
| Day 6 | main.py | `feat: complete CLI screening pipeline` |
| Day 7 | dashboard.py | `feat: Streamlit dashboard with Plotly charts` |
| Day 8 | README.md, docs/ | `docs: full README and interview prep guide` |

## GitHub Repository Tags

Add these topics to your repo (Settings → Topics):
```
python, nlp, machine-learning, tfidf, resume-screening, ats,
streamlit, scikit-learn, hr-tech, automation, data-analysis, portfolio-project
```

## Screenshots to Upload (images/ folder)

1. `01_folder_structure.png` — VS Code showing all files
2. `02_terminal_output.png` — Running main.py, ranked table output
3. `03_dashboard_home.png` — Streamlit home screen
4. `04_dashboard_results.png` — Rankings tab with candidate cards
5. `05_dashboard_charts.png` — Charts tab with bar and pie charts
6. `06_csv_output.png` — Generated CSV file open in Excel
7. `07_candidate_detail.png` — Detail view of top candidate

Upload with:
```bash
git add images/
git commit -m "docs: add project screenshots"
git push
```
