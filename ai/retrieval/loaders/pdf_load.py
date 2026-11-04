import os

import logfire
from pypdf import PdfReader


def parse_pdf(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a PDF file using pypdf."""
    with logfire.span("parse_pdf", file_name=file_name):
        try:
            reader = PdfReader(file_name)
            pages = reader.pages
            total_pages = len(pages)

            text_parts = []
            for i, page in enumerate(pages):
                text = page.extract_text() or ""
                if text:
                    text_parts.append(text)

            full_text = "\n".join(text_parts)

            # Extract PDF document info metadata
            pdf_meta = reader.metadata or {}
            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "pdf",
                "total_pages": total_pages,
                "extracted_pages": len(text_parts),
                "total_characters": len(full_text),
                "title": getattr(pdf_meta, "title", None),
                "author": getattr(pdf_meta, "author", None),
                "subject": getattr(pdf_meta, "subject", None),
                "creator": getattr(pdf_meta, "creator", None),
            }
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            logfire.info(
                "PDF parsing completed",
                file_name=file_name,
                total_pages=total_pages,
                extracted_pages=len(text_parts),
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception("Error parsing PDF {file_name}: {error}", file_name=file_name, error=str(e))
            raise
