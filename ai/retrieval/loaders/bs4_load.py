import os

import logfire
from bs4 import BeautifulSoup


def parse_html(file_name: str) -> tuple[str, dict]:
    """Extract full text and metadata from an HTML file using BeautifulSoup."""
    with logfire.span("parse_html", file_name=file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Extract metadata before stripping tags
            title = soup.title.string.strip() if soup.title and soup.title.string else None
            meta_desc = None
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and meta_tag.get("content"):
                meta_desc = meta_tag["content"].strip()
            meta_author = None
            author_tag = soup.find("meta", attrs={"name": "author"})
            if author_tag and author_tag.get("content"):
                meta_author = author_tag["content"].strip()
            meta_lang = None
            html_tag = soup.find("html")
            if html_tag and html_tag.get("lang"):
                meta_lang = html_tag["lang"]

            # Remove script and style elements that don't contain useful text
            for element in soup(["script", "style", "meta", "link"]):
                element.decompose()

            full_text = soup.get_text(separator="\n", strip=True)

            metadata = {
                "source": file_name,
                "file_name": os.path.basename(file_name),
                "file_size": os.path.getsize(file_name),
                "file_type": "html",
                "total_characters": len(full_text),
                "title": title,
                "description": meta_desc,
                "author": meta_author,
                "language": meta_lang,
            }
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            logfire.info(
                "HTML parsing completed",
                file_name=file_name,
                total_characters=len(full_text),
            )
            return full_text, metadata
        except Exception as e:
            logfire.exception(
                "Error parsing HTML {file_name}: {error}",
                file_name=file_name,
                error=str(e),
            )
            raise
