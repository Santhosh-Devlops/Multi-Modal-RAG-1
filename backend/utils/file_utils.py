import os
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from config import UPLOADS_DIR, EXTRACTED_IMAGES_DIR, EXTRACTED_TABLES_DIR

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"}

def is_allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS

def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower().replace(".", "")

def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def save_uploaded_file(file_obj, filename: str) -> str:
    """Save an incoming file upload safely to the uploads directory."""
    target_path = UPLOADS_DIR / filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file_obj, buffer)
    return str(target_path)

def render_pdf_page_preview(pdf_path: str, page_number: int, doc_id: int) -> str:
    """Render a high-quality preview image of a PDF page and return its relative path."""
    try:
        doc = fitz.open(pdf_path)
        if 0 <= page_number - 1 < len(doc):
            page = doc[page_number - 1]
            pix = page.get_pixmap(dpi=150)
            preview_filename = f"preview_doc_{doc_id}_page_{page_number}.png"
            preview_path = EXTRACTED_IMAGES_DIR / preview_filename
            pix.save(str(preview_path))
            doc.close()
            return f"/api/static/images/{preview_filename}"
        doc.close()
    except Exception as e:
        print(f"Error generating page preview: {e}")
    return ""
