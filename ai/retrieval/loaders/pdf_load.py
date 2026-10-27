import logfire
from pypdf import PdfReader


def parse_pdf(file_name: str) -> str:
    """Extract full text from a PDF file using pypdf."""
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
            logfire.info(
                "PDF parsing completed",
                file_name=file_name,
                total_pages=total_pages,
                extracted_pages=len(text_parts),
                total_characters=len(full_text),
            )
            return full_text
        except Exception as e:
            logfire.exception("Error parsing PDF {file_name}: {error}", file_name=file_name, error=str(e))
            raise