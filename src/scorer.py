"""
scorer.py
---------
Core scoring engine:
  1. TF-IDF vectorization of resume + job description
  2. Cosine similarity score (0–100)
  3. Keyword/skill match score
  4. Final weighted composite score
  5. Shortlist decision
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ─────────────────────────────────────────────
# WEIGHTS FOR COMPOSITE SCORE
# ─────────────────────────────────────────────
TFIDF_WEIGHT    = 0.50   # 50% from semantic similarity
SKILL_WEIGHT    = 0.40   # 40% from direct skill keyword matches
EXPERIENCE_W    = 0.10   # 10% from experience keywords

SHORTLIST_THRESHOLD = 55.0  # Score >= 55 → Shortlisted


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute cosine similarity between resume and job description
    using TF-IDF vectors.
    Returns: score between 0 and 100.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # unigrams + bigrams for better matching
        min_df=1,
        stop_words="english"
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception as e:
        print(f"[TF-IDF ERROR] {e}")
        return 0.0


def compute_skill_match_score(resume_text: str, required_skills: list) -> dict:
    """
    Check how many required skills appear in the resume text.
    Returns: {score, matched_skills, missing_skills, match_percentage}
    """
    resume_lower = resume_text.lower()
    matched = []
    missing = []

    for skill in required_skills:
        skill_lower = skill.lower().strip()
        # Use word boundary matching for accuracy
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, resume_lower):
            matched.append(skill)
        else:
            missing.append(skill)

    total = len(required_skills)
    match_pct = (len(matched) / total * 100) if total > 0 else 0.0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_count": len(matched),
        "total_skills": total,
        "skill_match_pct": round(match_pct, 2)
    }


def compute_experience_score(resume_text: str) -> float:
    """
    Heuristic experience scoring based on keywords in resume.
    Awards bonus points for seniority/experience indicators.
    Returns: score between 0 and 100.
    """
    resume_lower = resume_text.lower()
    score = 0.0

    # Check for experience mentions
    experience_keywords = {
        "years of experience": 30,
        "year experience": 25,
        "intern": 15,
        "internship": 15,
        "worked at": 20,
        "employed": 20,
        "developer": 20,
        "engineer": 20,
        "analyst": 20,
        "manager": 25,
        "lead": 20,
        "senior": 30,
        "junior": 10,
        "fresher": 5,
    }

    for kw, pts in experience_keywords.items():
        if kw in resume_lower:
            score = max(score, pts)  # take the highest match

    # Also check for explicit year patterns: "2 years", "3+ years"
    year_pattern = re.findall(r"(\d+)\+?\s*year", resume_lower)
    if year_pattern:
        max_years = max(int(y) for y in year_pattern)
        if max_years >= 3:
            score = max(score, 80.0)
        elif max_years >= 2:
            score = max(score, 60.0)
        elif max_years >= 1:
            score = max(score, 40.0)
        else:
            score = max(score, 20.0)

    return min(round(score, 2), 100.0)


def compute_composite_score(tfidf_score: float,
                             skill_match_pct: float,
                             experience_score: float) -> float:
    """
    Weighted composite score:
      Final = (TF-IDF × 0.50) + (Skill Match × 0.40) + (Experience × 0.10)
    Returns: score between 0 and 100.
    """
    composite = (
        tfidf_score    * TFIDF_WEIGHT +
        skill_match_pct * SKILL_WEIGHT +
        experience_score * EXPERIENCE_W
    )
    return round(composite, 2)


def shortlist_decision(score: float) -> str:
    """Map score to decision label."""
    if score >= 75:
        return "Strongly Shortlisted"
    elif score >= SHORTLIST_THRESHOLD:
        return "Shortlisted"
    elif score >= 35:
        return "Maybe (Review Manually)"
    else:
        return "Rejected"


def score_resume(resume_text: str,
                 cleaned_resume: str,
                 jd_text: str,
                 required_skills: list,
                 candidate_name: str = "Unknown",
                 filename: str = "") -> dict:
    """
    Master scoring function. Combines all scoring components.
    Returns: full scoring result dictionary.
    """
    # Component scores
    tfidf_score     = compute_tfidf_similarity(cleaned_resume, jd_text)
    skill_result    = compute_skill_match_score(resume_text, required_skills)
    experience_score = compute_experience_score(resume_text)

    # Final score
    final_score = compute_composite_score(
        tfidf_score,
        skill_result["skill_match_pct"],
        experience_score
    )

    decision = shortlist_decision(final_score)

    return {
        "filename": filename,
        "candidate_name": candidate_name,
        "tfidf_score": tfidf_score,
        "skill_match_pct": skill_result["skill_match_pct"],
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "matched_count": skill_result["matched_count"],
        "total_skills": skill_result["total_skills"],
        "experience_score": experience_score,
        "final_score": final_score,
        "decision": decision
    }


if __name__ == "__main__":
    # Quick unit test
    resume = "Python developer with 3 years experience in pandas numpy scikit-learn machine learning"
    jd = "Looking for Python developer with pandas scikit-learn machine learning experience"
    skills = ["Python", "Pandas", "Scikit-learn", "Machine Learning", "Docker"]

    result = score_resume(resume, resume, jd, skills, "Test Candidate", "test.txt")
    for k, v in result.items():
        print(f"{k:25}: {v}")
