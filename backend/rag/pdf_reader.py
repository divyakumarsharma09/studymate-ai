import pymupdf


def extract_pages(pdf_path: str) -> list:
    pages = []
    doc = pymupdf.open(pdf_path)
    for number, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            pages.append({"page": number, "text": text})
    doc.close()
    return pages