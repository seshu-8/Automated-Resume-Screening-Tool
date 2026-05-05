"""
main.py
-------
Automated Resume Screening Tool — Main Pipeline
================================================
Run: python main.py

Flow:
  1. Load job descriptions from data/job_descriptions.json
  2. User selects a job
  3. Load all resumes from resumes/ folder
  4. Extract text → Clean → Score → Rank
  5. Generate CSV + JSON reports in outputs/
  6. Print ranked table to terminal
"""

import os
import sys
import json

# ─── Add src/ to path ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from text_extractor   import load_all_resumes
from text_cleaner     import clean_text, extract_candidate_name, extract_email
from scorer           import score_resume
from report_generator import (generate_csv_report, generate_json_report,
                               print_ranked_table, generate_summary_stats)


# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESUME_DIR  = os.path.join(BASE_DIR, "resumes")
DATA_DIR    = os.path.join(BASE_DIR, "data")
OUTPUT_DIR  = os.path.join(BASE_DIR, "outputs")
JD_FILE     = os.path.join(DATA_DIR, "job_descriptions.json")


def load_job_descriptions() -> list:
    """Load job descriptions from JSON file."""
    if not os.path.exists(JD_FILE):
        print(f"[ERROR] Job descriptions file not found: {JD_FILE}")
        sys.exit(1)
    with open(JD_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("jobs", [])


def select_job(jobs: list) -> dict:
    """Let user select a job description interactively."""
    print("\n" + "="*60)
    print("  AUTOMATED RESUME SCREENING TOOL")
    print("="*60)
    print("\nAvailable Job Descriptions:\n")

    for i, job in enumerate(jobs, start=1):
        print(f"  [{i}] {job['title']} — {job['company']}")
        print(f"      Required Skills: {', '.join(job['required_skills'][:5])}...")
        print()

    while True:
        try:
            choice = int(input("Select job number: ").strip())
            if 1 <= choice <= len(jobs):
                return jobs[choice - 1]
            else:
                print(f"Enter a number between 1 and {len(jobs)}")
        except ValueError:
            print("Please enter a valid number.")


def run_screening(job: dict) -> list:
    """Run full screening pipeline for the selected job."""
    print(f"\n[JOB SELECTED] {job['title']} — {job['company']}")
    print(f"Required Skills: {', '.join(job['required_skills'])}\n")

    # 1. Load resumes
    print("[STEP 1] Loading resumes...")
    raw_resumes = load_all_resumes(RESUME_DIR)

    if not raw_resumes:
        print("[ERROR] No resumes found in 'resumes/' folder.")
        print("        Add .txt, .pdf, or .docx resume files and try again.")
        sys.exit(1)

    print(f"         Loaded {len(raw_resumes)} resume(s).\n")

    # Prepare JD text for TF-IDF
    jd_text = job["description"] + " " + " ".join(job["required_skills"])
    jd_clean = clean_text(jd_text)

    # 2. Process each resume
    print("[STEP 2] Extracting, cleaning, and scoring resumes...")
    results = []

    for filename, raw_text in raw_resumes.items():
        # Extract metadata
        candidate_name = extract_candidate_name(raw_text)
        email          = extract_email(raw_text)

        # Clean text
        cleaned_text = clean_text(raw_text)

        # Score
        result = score_resume(
            resume_text    = raw_text,
            cleaned_resume = cleaned_text,
            jd_text        = jd_clean,
            required_skills= job["required_skills"],
            candidate_name = candidate_name,
            filename       = filename
        )
        result["email"] = email
        results.append(result)
        print(f"  ✓ {filename:<40} Score: {result['final_score']:.1f}  →  {result['decision']}")

    return results


def save_reports(results: list, job: dict):
    """Save CSV and JSON reports."""
    safe_title = job["title"].replace(" ", "_").replace("/", "-")
    timestamp  = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name  = f"{safe_title}_{timestamp}"

    csv_path  = os.path.join(OUTPUT_DIR, f"{base_name}.csv")
    json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_csv_report(results, csv_path, job["title"])
    generate_json_report(results, json_path)

    return csv_path, json_path


def main():
    # Load jobs
    jobs = load_job_descriptions()

    # Select job
    selected_job = select_job(jobs)

    # Run screening
    results = run_screening(selected_job)

    # Print ranked table
    print_ranked_table(results, selected_job["title"])

    # Save reports
    csv_path, json_path = save_reports(results, selected_job)

    # Summary
    stats = generate_summary_stats(results)
    print(f"\n[DONE] Reports saved:")
    print(f"       CSV  → {csv_path}")
    print(f"       JSON → {json_path}")
    print(f"\n[STATS] Avg Score: {stats['avg_score']} | Top: {stats['top_candidate']}\n")


if __name__ == "__main__":
    main()
