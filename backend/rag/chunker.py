def split_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(pages: list) -> list:
    chunks = []
    for page in pages:
        for piece in split_text(page["text"]):
            chunks.append({"page": page["page"], "text": piece})
    return chunks