from pypdf import PdfReader



def parse_pdf(file_name:str):
    
    reader=PdfReader(file_name)

    pages = reader.pages
    total_pages = len(pages)

    text_parts= []
    for page in pages:

        text= page.extract_text() or ""

        if text:
            text_parts.append(text)

    full_text= "\n".join(text_parts)

    return full_text