import csv
import os

import logfire


def parse_csv(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a CSV file, converting each row into a readable line."""
    with logfire.span("parse_csv", file_name=file_name):
        try:
            with open(file_name, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                metadata = {
                    "source": file_name,
                    "file_name": os.path.basename(file_name),
                    "file_size": os.path.getsize(file_name),
                    "file_type": "csv",
                    "total_rows": 0,
                    "total_columns": 0,
                    "headers": [],
                    "total_characters": 0,
                }
                logfire.info(
                    "CSV parsing completed (empty file)",
                    file_name=file_name,
                    total_characters=0,
                )
                return "", metadata

            headers = [h.strip() for h in rows[0]]
            text_parts = []

            if len(rows) > 1:
                # Format each data row as "header1: value1, header2: value2, ..."
                for row in rows[1:]:
                    row_parts = []
                    for i, cell in enumerate(row):
                        cell = cell.strip()
                        if cell:
                            header = headers[i] if i < len(headers) else f"column_{i}"
                            row_parts.append(f"{header}: {cell}")
                    if row_parts:
                        text_parts.append(", ".join(row_parts))
            else:
                # Only headers, no data rows
                text_parts.append(", ".join(h for h in headers if h))

            full_text = "\n".join(text_parts)

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "csv",
                "total_rows": len(rows) - 1,
                "total_columns": len(headers),
                "headers": headers,
                "total_characters": len(full_text),
            }

            logfire.info(
                "CSV parsing completed",
                file_name=file_name,
                total_rows=len(rows) - 1,
                total_columns=len(headers),
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing CSV {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise
