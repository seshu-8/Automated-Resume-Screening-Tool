"""
text_cleaner.py
---------------
Cleans and preprocesses raw resume text for NLP processing.
Steps: lowercase → remove noise → tokenize → remove stopwords → stem/lemmatize
"""

import re
import string

# Comprehensive built-in stopwords (no NLTK download needed)
NLTK_AVAILABLE = False
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "these",
    "those", "am", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "having", "do", "does", "did", "doing", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "also", "well", "also", "also", "get", "got", "getting",
    "seek", "seeking", "looking", "looking", "work", "working"
}

# Try NLTK stemmer (optional enhancement)
try:
    from nltk.stem import PorterStemmer
    import nltk
    stemmer = PorterStemmer()
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline for resume text.
    Returns: cleaned, lowercased, stopword-removed text string.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # 3. Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # 4. Remove phone numbers
    text = re.sub(r"[\+\(]?[1-9][0-9\-\(\) ]{7,}[0-9]", " ", text)

    # 5. Remove special characters (keep alphanumeric + spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # 6. Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # 7. Tokenize
    tokens = text.split()

    # 8. Remove stopwords + short tokens (< 2 chars)
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

    # 9. Optional stemming (for better keyword matching)
    if NLTK_AVAILABLE:
        tokens = [stemmer.stem(t) for t in tokens]

    return " ".join(tokens)


def extract_email(text: str) -> str:
    """Extract email address from raw text."""
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else "N/A"


def extract_phone(text: str) -> str:
    """Extract phone number from raw text."""
    match = re.search(r"[\+\(]?[1-9][0-9\-\(\) ]{7,}[0-9]", text)
    return match.group(0).strip() if match else "N/A"


def extract_candidate_name(text: str) -> str:
    """
    Heuristic: first non-empty line is usually the candidate name.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        name = lines[0]
        # If line looks like a name (no special chars, < 50 chars)
        if len(name) < 50 and re.match(r"^[A-Za-z\s\.]+$", name):
            return name
    return "Unknown"


def preprocess_skills_list(skills: list) -> list:
    """
    Lowercase and strip whitespace from a list of skill strings.
    Used to normalize job description skills before matching.
    """
    return [s.lower().strip() for s in skills]


if __name__ == "__main__":
    sample = """
    Arjun Sharma
    Email: arjun@email.com | Phone: +91-9876543210
    Skills: Python, Pandas, NumPy, Machine Learning, Scikit-learn
    Experience: 2 years in Data Science at TCS
    """
    print("Original:")
    print(sample)
    print("\nCleaned:")
    print(clean_text(sample))
    print("\nEmail:", extract_email(sample))
    print("Phone:", extract_phone(sample))
    print("Name:", extract_candidate_name(sample))
