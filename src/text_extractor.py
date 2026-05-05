"""
text_extractor.py
-----------------
Handles text extraction from TXT, PDF, and DOCX resume files.
Supports fallback to plain text if PDF/DOCX libraries are missing.
"""

import os
import re

# ---------- Try importing PDF/DOCX libraries (optional) ----------
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False


def extract_text_from_txt(filepath: str) -> str:
    """Extract plain text from a .txt file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    if not PDF_SUPPORT:
        return "[PDF support not installed. Run: pip install pdfplumber]"
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from a .docx file using python-docx."""
    if not DOCX_SUPPORT:
        return "[DOCX support not installed. Run: pip install python-docx]"
    doc = Document(filepath)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def extract_text(filepath: str) -> str:
    """
    Master extractor — detects file type and calls the right function.
    Supports: .txt, .pdf, .docx
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        return extract_text_from_txt(filepath)
    elif ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".docx":
        return extract_text_from_docx(filepath)
    else:
        return f"[Unsupported file format: {ext}]"


def load_all_resumes(folder: str) -> dict:
    """
    Load all resumes from a folder.
    Returns: {filename: extracted_text}
    """
    resumes = {}
    supported = (".txt", ".pdf", ".docx")

    if not os.path.exists(folder):
        print(f"[ERROR] Resume folder not found: {folder}")
        return resumes

    for filename in os.listdir(folder):
        if filename.lower().endswith(supported):
            filepath = os.path.join(folder, filename)
            text = extract_text(filepath)
            if text.strip():
                resumes[filename] = text
                print(f"[LOADED] {filename} ({len(text)} chars)")
            else:
                print(f"[EMPTY]  {filename} — no text extracted")

    return resumes


if __name__ == "__main__":
    # Quick test
    resumes = load_all_resumes("../resumes")
    for name, text in resumes.items():
        print(f"\n{'='*50}")
        print(f"FILE: {name}")
        print(text[:300])
