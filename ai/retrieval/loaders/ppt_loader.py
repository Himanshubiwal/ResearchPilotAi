import os
import logfire
from pptx import Presentation


def parse_pptx(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a PPTX file using python-pptx."""
    with logfire.span("parse_pptx", file_name=file_name):
        try:
            prs = Presentation(file_name)
            total_slides = len(prs.slides)
            text_parts = []
            extracted_slides = 0

            for slide_num, slide in enumerate(prs.slides, start=1):
                slide_texts = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            text = paragraph.text.strip()
                            if text:
                                slide_texts.append(text)
                    elif shape.has_table:
                        for row in shape.table.rows:
                            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if row_cells:
                                slide_texts.append(" | ".join(row_cells))

                if slide_texts:
                    extracted_slides += 1
                    text_parts.append(f"--- Slide {slide_num} ---\n" + "\n".join(slide_texts))

            full_text = "\n\n".join(text_parts)

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "pptx",
                "total_slides": total_slides,
                "extracted_slides": extracted_slides,
                "total_characters": len(full_text),
            }

            logfire.info(
                "PPTX parsing completed",
                file_name=file_name,
                total_slides=total_slides,
                extracted_slides=extracted_slides,
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing PPTX {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise
