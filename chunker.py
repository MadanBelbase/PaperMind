import re

class AcademicTextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:st
        clean_text = re.sub(r"\s+", " ", text).strip()
        chunks = []
        start = 0
        text_len = len(clean_text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len:
                boundary = max(clean_text.rfind(". ", start, end), clean_text.rfind("? ", start, end))
                if boundary != -1 and boundary > start + self.chunk_overlap:
                    end = boundary + 1

            chunk = clean_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def create_documents(self, text: str, source_name: str) -> list[dict]:
        raw_chunks = self.split_text(text)
        return [
            {
                "text": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_id": index,
                    "length": len(chunk)
                }
            }
            for index, chunk in enumerate(raw_chunks)
        ]
