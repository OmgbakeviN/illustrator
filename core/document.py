"""
Modèle de document extrêmement simplifié pour l'étape 0.
- Contient un titre, une taille de canvas et une liste de 'shapes' (que l'on ajoutera plus tard).
- Fournit des méthodes de (dé)serialisation dict pour la sauvegarde.
"""

from dataclasses import dataclass, field

@dataclass
class Document:
    title: str = "Sans titre"
    width: int = 1200         # largeur canvas (px)
    height: int = 800         # hauteur canvas (px)
    shapes: list = field(default_factory=list)  # sera rempli à l'étape suivante

    def clear(self):
        """Réinitialise le contenu du document (utile pour un 'Nouveau')."""
        self.title = "Sans titre"
        self.shapes.clear()

    # --- Sérialisation basique (JSON-ready) ---
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "shapes": self.shapes,  # pour l'instant vide
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        doc = cls()
        doc.title = data.get("title", "Sans titre")
        doc.width = int(data.get("width", 1200))
        doc.height = int(data.get("height", 800))
        doc.shapes = list(data.get("shapes", []))
        return doc
