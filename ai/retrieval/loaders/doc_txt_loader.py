import os

import logfire
import docx2txt


def parse_docx(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a DOCX file using docx2txt."""
    with logfire.span("parse_docx", file_name=file_name):
        try:
            text = docx2txt.process(file_name)
            full_text = text.strip() if text else ""

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "docx",
                "total_characters": len(full_text),
            }

            logfire.info(
                "DOCX parsing completed",
                file_name=file_name,
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing DOCX {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise


def parse_txt(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a plain text file."""
    with logfire.span("parse_txt", file_name=file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                full_text = f.read()

            total_lines = full_text.count("\n") + 1 if full_text else 0

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "txt",
                "total_lines": total_lines,
                "total_characters": len(full_text),
            }

            logfire.info(
                "TXT parsing completed",
                file_name=file_name,
                total_lines=total_lines,
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing TXT {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise
