"""Bounded, transparent lexical retrieval over curated local documents."""

from dataclasses import dataclass
from pathlib import Path
import re

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
STOP_WORDS = {"the", "a", "an", "of", "is", "i", "my", "me", "to", "what", "how", "and", "it"}


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP_WORDS


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


class Retriever:
    def __init__(self, directory: Path = KNOWLEDGE_DIR):
        documents = []
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise ValueError(f"Empty knowledge document: {path.name}")
            documents.append(Document(path.stem, text.splitlines()[0].lstrip("# "), text))
        self.documents = tuple(documents)
        if not self.documents:
            raise ValueError("No knowledge documents found; restore the knowledge/ folder.")

    def retrieve(self, question: str, intent: str, limit: int = 2) -> tuple[Document, ...]:
        query = tokens(question)
        primary = {"probability": "probability", "strategy": "strategy", "hint": "strategy", "rules": "rules"}[intent]
        if not any(doc.id == primary for doc in self.documents):
            raise ValueError(f"Missing required reference: {primary}")
        companion = "strategy" if intent == "probability" else "probability"
        scores = [
            (len(query & tokens(doc.text)) + (10 if doc.id == companion else 0), doc)
            for doc in self.documents
        ]
        scores.sort(key=lambda item: (item[1].id != primary, -item[0], item[1].id))
        return tuple(doc for score, doc in scores[:limit] if score > 0 or doc.id == primary)
