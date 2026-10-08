import hashlib
import re


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_content_hash(text: str) -> str:
    normalized_text = normalize_text(text)

    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
