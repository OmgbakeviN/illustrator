"""
Document gère la liste de formes.
On ajoute :
 - add_shape(), remove_shape()
 - to_dict() / from_dict() mis à jour pour stocker les formes
"""

from dataclasses import dataclass, field
from core.shapes import Shape, shape_from_dict

@dataclass
class Document:
    title: str = "Sans titre"
    width: int = 1200
    height: int = 800
    shapes: list[Shape] = field(default_factory=list)

    def clear(self):
        self.shapes.clear()

    def add_shape(self, shape: Shape):
        self.shapes.append(shape)

    def remove_shape(self, shape: Shape):
        self.shapes.remove(shape)

    def to_dict(self):
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "shapes": [s.to_dict() for s in self.shapes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        doc = cls(
            title=data.get("title", "Sans titre"),
            width=data.get("width", 1200),
            height=data.get("height", 800),
        )
        for sd in data.get("shapes", []):
            try:
                doc.shapes.append(shape_from_dict(sd))
            except Exception as e:
                print(f"Erreur chargement forme : {e}")
        return doc
