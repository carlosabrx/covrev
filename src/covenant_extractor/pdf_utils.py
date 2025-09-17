from __future__ import annotations

import os
from typing import List, Optional

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None  # type: ignore

def _extract_with_pdfminer(file_path: str) -> str:
    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Neither PyMuPDF nor pdfminer.six is available") from exc
    return extract_text(file_path) or ""


def extract_text_from_pdf(file_path: str, max_pages: Optional[int] = None) -> str:
    """
    Extract text from a PDF using PyMuPDF.

    - Adds clear page delimiters to aid section-boundary regex.
    - If max_pages is provided, reads up to that many pages.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if fitz is None:
        # Fallback to pdfminer whole-document extraction without page headers
        return _extract_with_pdfminer(file_path)

    document = fitz.open(file_path)
    try:
        extracted_pages: List[str] = []
        for page_index, page in enumerate(document):
            if max_pages is not None and page_index >= max_pages:
                break
            page_text = page.get_text("text")
            header = f"\n\n=== [PAGE {page_index + 1}] ===\n\n"
            extracted_pages.append(header + (page_text or ""))
        return "".join(extracted_pages).strip()
    finally:
        document.close()


def extract_text_by_page(file_path: str, max_pages: Optional[int] = None) -> List[str]:
    """Return a list of page texts for finer-grained processing if needed."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if fitz is None:
        # pdfminer fallback returns one string; split roughly by form feed markers if present
        text = _extract_with_pdfminer(file_path)
        chunks = text.split("\f")
        if max_pages is not None:
            chunks = chunks[:max_pages]
        return chunks

    document = fitz.open(file_path)
    try:
        pages: List[str] = []
        for page_index, page in enumerate(document):
            if max_pages is not None and page_index >= max_pages:
                break
            pages.append(page.get_text("text") or "")
        return pages
    finally:
        document.close()
