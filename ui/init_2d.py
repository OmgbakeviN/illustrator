"""
Canvas 2D avec :
- Rendu des formes du Document
- Pan/Zoom (molette = zoom, clic droit drag = pan)
- Dispatch des évènements vers l'outil actif (Select/Rect/Ellipse/Line)
- Suppression de la sélection avec 'Suppr'

Coordonnées :
- On maintient (self.scale, self.offset_x, self.offset_y).
- Les événements souris (en pixels widget) sont convertis en coords CANVAS.
"""

from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QPainter, QFont, QWheelEvent, QTransform
from PyQt6.QtWidgets import QWidget

from ui.tools import SelectTool, RectTool, EllipseTool, LineTool

class Canvas2D(QWidget):
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self._document = document
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setStyleSheet("background: #2b2b2b;")

        # Pan/zoom
        self.scale = 1.0
        self.offset_x = 24.0
        self.offset_y = 24.0
        self._panning = False
        self._pan_start = None

        # Outils
        self.tools = {
            "select": SelectTool(self),
            "rect": RectTool(self),
            "ellipse": EllipseTool(self),
            "line": LineTool(self),
        }
        self.active_tool = self.tools["select"]

        # Sélection courante (référence sur une Shape)
        self.selected = None

    @property
    def doc(self):
        """Accès public au document (alias de _document)."""
        return self._document


    # --------- API utilisée par MainWindow ---------
    def set_document(self, document):
        self._document = document
        self.selected = None
        self.update()

    def set_tool(self, name: str):
        self.active_tool = self.tools[name]
        self.setCursor(Qt.CursorShape.ArrowCursor if name == "select" else Qt.CursorShape.CrossCursor)
        self.update()

    def zoom_reset(self):
        self.scale = 1.0
        self.offset_x = 24.0
        self.offset_y = 24.0
        self.update()

    def zoom_in(self):
        self.scale *= 1.1
        self.update()

    def zoom_out(self):
        self.scale /= 1.1
        self.update()

    # --------- conversions coordonnées ---------
    def widget_to_canvas(self, pt) -> QPointF:
        """Convertit un QPoint (pixels widget) vers coords canvas (après pan/zoom)."""
        x = (pt.x() - self.offset_x) / self.scale
        y = (pt.y() - self.offset_y) / self.scale
        return QPointF(x, y)

    # --------- rendu ---------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # papier (blanc) avec transformation pan/zoom
        p.fillRect(self.rect(), Qt.GlobalColor.black)  # bordure extérieure
        p.save()
        t = QTransform()
        t.translate(self.offset_x, self.offset_y)
        t.scale(self.scale, self.scale)
        p.setTransform(t)

        # page
        from PyQt6.QtCore import QRectF
        page_rect = QRectF(0, 0, max(100, self._document.width // 2), max(80, self._document.height // 2))
        p.fillRect(page_rect, Qt.GlobalColor.white)

        # dessiner toutes les formes
        for s in self._document.shapes:
            s.draw(p)

        # overlay de l'outil (poignées, previews…)
        self.active_tool.draw_overlay(p)

        p.restore()

        # titre en haut à gauche (non zoomé)
        p.setPen(Qt.GlobalColor.white)
        p.setFont(QFont("Inter", 11))
        p.drawText(10, 18, f"Outil: {self._tool_name()} | Zoom: {int(self.scale*100)}%")

    def _tool_name(self):
        for k, v in self.tools.items():
            if v is self.active_tool:
                return k
        return "?"

    # --------- souris / clavier ---------
    def wheelEvent(self, ev: QWheelEvent):
        # zoom autour du pointeur
        old = self.scale
        if ev.angleDelta().y() > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        # ajuster l'offset pour zoomer autour du curseur
        pos_w = ev.position()
        pt_canvas = self.widget_to_canvas(pos_w)
        cx, cy = pt_canvas.x(), pt_canvas.y()
        self.offset_x = pos_w.x() - cx * self.scale
        self.offset_y = pos_w.y() - cy * self.scale

        self.update()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton:
            # PAN avec clic droit
            self._panning = True
            self._pan_start = ev.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        pos = self.widget_to_canvas(ev.position())
        self.active_tool.on_mouse_press(pos, ev)

    def mouseMoveEvent(self, ev):
        if self._panning:
            delta = ev.position() - self._pan_start
            self._pan_start = ev.position()
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.update()
            return

        pos = self.widget_to_canvas(ev.position())
        self.active_tool.on_mouse_move(pos, ev)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton and self._panning:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        pos = self.widget_to_canvas(ev.position())
        self.active_tool.on_mouse_release(pos, ev)

    def keyPressEvent(self, ev):
        # Delete -> supprime la sélection
        if ev.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.selected and self.selected in self._document.shapes:
                self._document.remove_shape(self.selected)
                self.selected = None
                self.update()
        else:
            super().keyPressEvent(ev)
