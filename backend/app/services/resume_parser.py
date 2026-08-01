from pypdf import PdfReader

def _sanitize_text(text):
    """
    Removes lone/invalid surrogate characters that some PDFs produce during
    text extraction (often from icon glyphs or unusual embedded fonts).
    These are technically valid in a Python string but crash when encoding
    to UTF-8 for the database.
    """
    return text.encode("utf-8", errors="ignore").decode("utf-8")


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        raw_text = "\n".join(text_parts).strip()
        return _sanitize_text(raw_text)
    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return ""