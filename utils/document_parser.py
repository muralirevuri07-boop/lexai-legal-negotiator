import io
from pathlib import Path
from typing import Union
import pdfplumber
import pypdf
from utils.logger import app_logger

def extract_text_from_pdf(file):
    text = ""
    try:
        if isinstance(file, (str, Path)):
            with open(file, "rb") as f:
                file = f.read()
        with pdfplumber.open(io.BytesIO(file)) as pdf:
            pages = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    pages.append(f"[Page {page_num}]\n{page_text}")
            text = "\n\n".join(pages)
        if not text.strip():
            text = _extract_with_pypdf(file)
    except Exception as e:
        app_logger.error(f"PDF extraction failed: {e}")
        try:
            text = _extract_with_pypdf(file)
        except Exception as e2:
            app_logger.error(f"pypdf fallback also failed: {e2}")
            text = ""
    return text

def _extract_with_pypdf(file_bytes):
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page_num, page in enumerate(reader.pages, 1):
        page_text = page.extract_text()
        if page_text:
            pages.append(f"[Page {page_num}]\n{page_text}")
    return "\n\n".join(pages)

def clean_contract_text(text):
    if not text:
        return ""
    lines = text.split("\n")
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            cleaned_lines.append(stripped)
            prev_blank = False
    return "\n".join(cleaned_lines).strip()