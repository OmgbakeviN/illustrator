"""
Sauvegarde/chargement du Document au format JSON.
À ce stade, on manipule seulement les champs simples du Document.
"""

import json
from core.document import Document

def save_document(doc: Document, path: str) -> None:
    """Écrit le document sur disque au format JSON lisible."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc.to_dict(), f, ensure_ascii=False, indent=2)

def load_document(path: str) -> Document:
    """Charge un document JSON depuis le disque."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Document.from_dict(data)
