"""
report_generator.py
-------------------
Generates screening reports:
  - CSV report with all candidates ranked
  - Summary stats (shortlisted vs rejected)
  - Console-friendly ranked table
"""

import os
import csv
import json
from datetime import datetime


def generate_csv_report(results: list, output_path: str, job_title: str = "") -> str:
    """
    Write all scored candidates to a CSV file, sorted by final_score desc.
    Returns: path to CSV file.
    """
    if not results:
        print("[REPORT] No results to write.")
        return ""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Sort by final score descending
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    # Add rank
    for i, r in enumerate(sorted_results, start=1):
        r["rank"] = i

    fieldnames = [
        "rank", "filename", "candidate_name",
        "final_score", "tfidf_score", "skill_match_pct",
        "matched_count", "total_skills", "experience_score",
        "decision", "matched_skills", "missing_skills"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in sorted_results:
            # Convert lists to readable strings
            row["matched_skills"] = ", ".join(row.get("matched_skills", []))
            row["missing_skills"] = ", ".join(row.get("missing_skills", []))
            writer.writerow(row)

    print(f"[REPORT] CSV saved → {output_path}")
    return output_path


def generate_json_report(results: list, output_path: str) -> str:
    """Save full results as JSON for API/dashboard use."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_candidates": len(results),
        "shortlisted": sum(1 for r in results if "Shortlisted" in r["decision"]),
        "rejected": sum(1 for r in results if r["decision"] == "Rejected"),
        "results": sorted_results
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"[REPORT] JSON saved → {output_path}")
    return output_path


def print_ranked_table(results: list, job_title: str = ""):
    """Print a clean ranked table to the terminal."""
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    print("\n" + "=" * 80)
    print(f"  RESUME SCREENING RESULTS  |  Job: {job_title}")
    print("=" * 80)
    print(f"{'RANK':<5} {'CANDIDATE':<22} {'SCORE':>7} {'SKILL %':>8} {'TF-IDF':>8}  DECISION")
    print("-" * 80)

    for i, r in enumerate(sorted_results, start=1):
        name = r.get("candidate_name", r.get("filename", ""))[:20]
        score = r["final_score"]
        skill = r["skill_match_pct"]
        tfidf = r["tfidf_score"]
        decision = r["decision"]

        # Color-code by decision (terminal ANSI codes)
        if "Strongly" in decision:
            tag = "✅ " + decision
        elif "Shortlisted" in decision:
            tag = "✅ " + decision
        elif "Maybe" in decision:
            tag = "⚠️  " + decision
        else:
            tag = "❌ " + decision

        print(f"{i:<5} {name:<22} {score:>7.1f} {skill:>7.1f}% {tfidf:>7.1f}%  {tag}")

    print("=" * 80)
    shortlisted_count = sum(1 for r in results if "Shortlisted" in r["decision"])
    rejected_count    = sum(1 for r in results if r["decision"] == "Rejected")
    maybe_count       = sum(1 for r in results if "Maybe" in r["decision"])

    print(f"\n  SUMMARY: {len(results)} resumes processed")
    print(f"  ✅ Shortlisted : {shortlisted_count}")
    print(f"  ⚠️  Manual Review: {maybe_count}")
    print(f"  ❌ Rejected    : {rejected_count}")
    print("=" * 80 + "\n")


def generate_summary_stats(results: list) -> dict:
    """Return summary dictionary for dashboard use."""
    if not results:
        return {}

    scores = [r["final_score"] for r in results]
    return {
        "total": len(results),
        "shortlisted": sum(1 for r in results if "Shortlisted" in r["decision"]),
        "rejected": sum(1 for r in results if r["decision"] == "Rejected"),
        "maybe": sum(1 for r in results if "Maybe" in r["decision"]),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": round(max(scores), 2),
        "min_score": round(min(scores), 2),
        "top_candidate": max(results, key=lambda x: x["final_score"]).get("candidate_name", "N/A")
    }
