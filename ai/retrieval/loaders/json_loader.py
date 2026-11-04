import json
import os

import logfire


def parse_json(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from a JSON file by recursively collecting all string values."""
    with logfire.span("parse_json", file_name=file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            text_parts = []
            _extract_text(data, text_parts)
            full_text = "\n".join(text_parts)

            # Determine top-level structure info
            if isinstance(data, list):
                structure = "array"
                top_level_items = len(data)
            elif isinstance(data, dict):
                structure = "object"
                top_level_items = len(data)
            else:
                structure = type(data).__name__
                top_level_items = 1

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "json",
                "structure": structure,
                "top_level_items": top_level_items,
                "total_values_extracted": len(text_parts),
                "total_characters": len(full_text),
            }

            logfire.info(
                "JSON parsing completed",
                file_name=file_name,
                total_values=len(text_parts),
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing JSON {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise


def _extract_text(data, parts: list[str]) -> None:
    """Recursively extract all string values from a JSON structure."""
    if isinstance(data, str):
        stripped = data.strip()
        if stripped:
            parts.append(stripped)
    elif isinstance(data, dict):
        for key, value in data.items():
            # Include key-value context for better semantic meaning
            if isinstance(value, str) and value.strip():
                parts.append(f"{key}: {value.strip()}")
            else:
                _extract_text(value, parts)
    elif isinstance(data, list):
        for item in data:
            _extract_text(item, parts)
