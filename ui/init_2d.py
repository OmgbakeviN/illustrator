"""
Canvas 2D minimal.
- Pour l'étape 0 : on dessine juste un fond et un texte 'Canvas 2D'.
- On ajoutera le pan/zoom, les outils et le rendu des formes à l'étape 2.
"""

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtWidgets import QWidget

class Canvas2D(QWidget):
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self._document = document
        # Permet le focus clavier plus tard (raccourcis, delete, etc.)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        # Couleur de fond via style (optionnel)
        self.setStyleSheet("background: #2b2b2b;")

    # Accesseur pour remplacer le document quand on ouvre un fichier
    def set_document(self, document):
        self._document = document
        self.update()  # redessiner

    # Événement de peinture : QPainter dessine sur la surface du widget
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Fond ‘papier’ (gris très foncé déjà via stylesheet)
        # Ici on dessine un rectangle clair au centre simulant une page
        margin = 24
        page_rect = QRect(
            margin, margin,
            max(100, self._document.width // 2),
            max(80,  self._document.height // 2)
        )
        painter.fillRect(page_rect, Qt.GlobalColor.white)

        # Texte informatif
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Inter", 12))
        painter.drawText(page_rect, Qt.AlignmentFlag.AlignCenter, "Canvas 2D (Étape 0)")
