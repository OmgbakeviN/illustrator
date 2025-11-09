"""
Définition des formes de base (Rect, Ellipse, Line).
Chaque forme hérite de Shape et implémente :
  - draw(painter) : dessin sur le canvas
  - to_dict() / from_dict() : sérialisation JSON
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PyQt6.QtGui import QColor


# ------------------- CLASSE DE BASE -------------------
@dataclass
class Shape(ABC):
    x: float
    y: float
    w: float
    h: float
    stroke_color: str = "#000000"  # contour (hex)
    fill_color: str = "#FFFFFF"    # remplissage
    stroke_width: int = 2
    selected: bool = False         # utile pour l'étape 2 (sélection)

    @abstractmethod
    def draw(self, painter):
        """Dessine la forme avec QPainter."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Retourne une version JSON-serializable."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Recrée l’objet depuis un dict JSON."""
        pass


# ------------------- RECTANGLE -------------------
@dataclass
class RectShape(Shape):
    def draw(self, painter):
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPen, QBrush

        pen = QPen(QColor(self.stroke_color))
        pen.setWidth(self.stroke_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(self.fill_color)))
        painter.drawRect(QRectF(self.x, self.y, self.w, self.h))

        # Si sélectionné → cadre bleu
        if self.selected:
            painter.setPen(QPen(QColor("#00A2FF"), 1, 1))
            painter.setBrush(QBrush())
            painter.drawRect(QRectF(self.x - 3, self.y - 3, self.w + 6, self.h + 6))

    def to_dict(self):
        return {
            "type": "rect",
            "x": self.x, "y": self.y, "w": self.w, "h": self.h,
            "stroke_color": self.stroke_color,
            "fill_color": self.fill_color,
            "stroke_width": self.stroke_width
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ------------------- ELLIPSE -------------------
@dataclass
class EllipseShape(Shape):
    def draw(self, painter):
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPen, QBrush

        pen = QPen(QColor(self.stroke_color))
        pen.setWidth(self.stroke_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(self.fill_color)))
        painter.drawEllipse(QRectF(self.x, self.y, self.w, self.h))

    def to_dict(self):
        return {
            "type": "ellipse",
            "x": self.x, "y": self.y, "w": self.w, "h": self.h,
            "stroke_color": self.stroke_color,
            "fill_color": self.fill_color,
            "stroke_width": self.stroke_width
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ------------------- LIGNE -------------------
@dataclass
class LineShape(Shape):
    # pour une ligne, (x, y) est le point de départ, (x + w, y + h) le point de fin
    def draw(self, painter):
        from PyQt6.QtGui import QPen, QColor
        pen = QPen(QColor(self.stroke_color))
        pen.setWidth(self.stroke_width)
        painter.setPen(pen)
        painter.drawLine(int(self.x), int(self.y), int(self.x + self.w), int(self.y + self.h))

    def to_dict(self):
        return {
            "type": "line",
            "x": self.x, "y": self.y, "w": self.w, "h": self.h,
            "stroke_color": self.stroke_color,
            "stroke_width": self.stroke_width
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ------------------- FABRIQUE -------------------
def shape_from_dict(data: dict) -> Shape:
    """Fabrique une instance selon le champ 'type'."""
    t = data.get("type")
    if t == "rect":
        return RectShape.from_dict(data)
    elif t == "ellipse":
        return EllipseShape.from_dict(data)
    elif t == "line":
        return LineShape.from_dict(data)
    else:
        raise ValueError(f"Type de forme inconnu : {t}")
