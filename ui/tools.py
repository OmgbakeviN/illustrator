"""
Outils de dessin/édition pour le Canvas2D.

Chaque outil expose 4 méthodes utilisées par Canvas2D :
- on_mouse_press(pos, event)
- on_mouse_move(pos, event)
- on_mouse_release(pos, event)
- draw_overlay(painter) : dessine les aides visuelles (poignées, rect de création…)

Notes :
- 'pos' est toujours en coordonnées CANVAS (après transformation pan/zoom).
- L'outil a accès à 'canvas.doc' (Document) et 'canvas' pour demander un rafraîchissement.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor
from core.shapes import RectShape, EllipseShape, LineShape, Shape


# ------------------ OUTIL DE BASE ------------------
class Tool:
    def __init__(self, canvas):
        self.canvas = canvas

    # APIs appelées par Canvas2D
    def on_mouse_press(self, pos, ev): ...
    def on_mouse_move(self, pos, ev): ...
    def on_mouse_release(self, pos, ev): ...
    def draw_overlay(self, p): ...


# ------------------ OUTIL SELECTION ------------------
class SelectTool(Tool):
    """
    - Clic sur une forme → sélection.
    - Drag sur la forme → déplacement.
    - Drag sur une poignée → redimension.
    - Clic vide → désélection.
    - Suppr (géré dans Canvas2D.keyPressEvent) → supprime la forme sélectionnée.
    """

    HANDLE_SIZE = 8  # taille carrés bleus

    def __init__(self, canvas):
        super().__init__(canvas)
        self._dragging = False
        self._resizing = False
        self._drag_start = QPointF()
        self._orig = QPointF()     # position d'origine pour déplacement
        self._resize_handle = -1   # index de poignée

    # --------- utilitaires poignée ---------
    def _handles_for(self, s: Shape) -> list[QRectF]:
        """Retourne les 4 poignées (coins) pour Rect/Ellipse, 2 pour Line."""
        hs = self.HANDLE_SIZE
        if isinstance(s, LineShape):
            p1 = QPointF(s.x, s.y)
            p2 = QPointF(s.x + s.w, s.y + s.h)
            return [
                QRectF(p1.x() - hs/2, p1.y() - hs/2, hs, hs),
                QRectF(p2.x() - hs/2, p2.y() - hs/2, hs, hs),
            ]
        else:
            # coins du bounding box
            x, y, w, h = s.x, s.y, s.w, s.h
            return [
                QRectF(x - hs/2,       y - hs/2,       hs, hs),           # NW
                QRectF(x + w - hs/2,   y - hs/2,       hs, hs),           # NE
                QRectF(x + w - hs/2,   y + h - hs/2,   hs, hs),           # SE
                QRectF(x - hs/2,       y + h - hs/2,   hs, hs),           # SW
            ]

    def _hit_handle(self, s: Shape, pos: QPointF) -> int:
        """Retourne l'index de la poignée sous la souris, sinon -1."""
        for i, r in enumerate(self._handles_for(s)):
            if r.contains(pos):
                return i
        return -1

    def _hit_shape(self, pos: QPointF) -> Optional[Shape]:
        """Test très simple : bbox des Rect/Ellipse et distance pour les lignes."""
        for s in reversed(self.canvas.doc.shapes):  # du haut vers le bas
            if isinstance(s, LineShape):
                # distance point-segment (tolérance 6 px)
                import math
                ax, ay = s.x, s.y
                bx, by = s.x + s.w, s.y + s.h
                px, py = pos.x(), pos.y()
                # projection
                abx, aby = bx - ax, by - ay
                ab2 = abx*abx + aby*aby or 1.0
                t = max(0.0, min(1.0, ((px-ax)*abx + (py-ay)*aby) / ab2))
                cx, cy = ax + t*abx, ay + t*aby
                d = math.hypot(px - cx, py - cy)
                if d <= 6.0:
                    return s
            else:
                r = QRectF(s.x, s.y, s.w, s.h).normalized()
                if r.contains(pos):
                    return s
        return None

    # --------- évènements souris ---------
    def on_mouse_press(self, pos, ev):
        s = self.canvas.selected
        if s:
            idx = self._hit_handle(s, pos)
            if idx >= 0:
                # démarrage redimension
                self._resizing = True
                self._resize_handle = idx
                self._drag_start = QPointF(pos)
                return

        # sinon, test hit shape pour sélection/déplacement
        target = self._hit_shape(pos)
        # mettre à jour l’état sélection
        for sh in self.canvas.doc.shapes:
            sh.selected = (sh is target)
        self.canvas.selected = target
        self.canvas.update()

        if target:
            self._dragging = True
            self._drag_start = QPointF(pos)
            self._orig = QPointF(target.x, target.y)

    def on_mouse_move(self, pos, ev):
        s = self.canvas.selected
        if self._resizing and s:
            dx = pos.x() - self._drag_start.x()
            dy = pos.y() - self._drag_start.y()
            self._apply_resize(s, dx, dy, ev)
            self._drag_start = QPointF(pos)
            self.canvas.update()
            return

        if self._dragging and s:
            # déplacement
            dx = pos.x() - self._drag_start.x()
            dy = pos.y() - self._drag_start.y()
            s.x = self._orig.x() + dx
            s.y = self._orig.y() + dy
            self.canvas.update()

    def on_mouse_release(self, pos, ev):
        self._dragging = False
        self._resizing = False
        self._resize_handle = -1

    # --------- resize selon poignée ---------
    def _apply_resize(self, s: Shape, dx: float, dy: float, ev):
        if isinstance(s, LineShape):
            # 0 = P1, 1 = P2
            if self._resize_handle == 0:
                s.x += dx; s.y += dy
            else:
                s.w += dx; s.h += dy
            return

        # pour Rect/Ellipse
        # poignée: 0=NW,1=NE,2=SE,3=SW
        if self._resize_handle == 0:  # NW
            s.x += dx; s.y += dy; s.w -= dx; s.h -= dy
        elif self._resize_handle == 1:  # NE
            s.y += dy; s.w += dx; s.h -= dy
        elif self._resize_handle == 2:  # SE
            s.w += dx; s.h += dy
        elif self._resize_handle == 3:  # SW
            s.x += dx; s.w -= dx; s.h += dy

        # Contraintes Shift → carré/cercle
        if ev.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            side = min(abs(s.w), abs(s.h))
            # garder le coin d'origine selon la poignée
            if self._resize_handle == 0:  # NW fixe SE
                s.x = s.x + (s.w - side) if s.w < 0 else s.x
                s.y = s.y + (s.h - side) if s.h < 0 else s.y
                s.w = side if s.w >= 0 else -side
                s.h = side if s.h >= 0 else -side
            elif self._resize_handle == 1:  # NE fixe SW
                s.y = s.y + (s.h - side) if s.h < 0 else s.y
                s.w = side if s.w >= 0 else -side
                s.h = side if s.h >= 0 else -side
            elif self._resize_handle == 2:  # SE fixe NW
                s.w = side if s.w >= 0 else -side
                s.h = side if s.h >= 0 else -side
            elif self._resize_handle == 3:  # SW fixe NE
                s.x = s.x + (s.w - side) if s.w < 0 else s.x
                s.w = side if s.w >= 0 else -side
                s.h = side if s.h >= 0 else -side

    # --------- overlay (poignées) ---------
    def draw_overlay(self, p):
        s = self.canvas.selected
        if not s:
            return
        p.save()
        p.setPen(QPen(QColor("#00A2FF"), 1, Qt.PenStyle.DashLine))
        p.setBrush(QBrush())
        if isinstance(s, LineShape):
            p.drawLine(s.x, s.y, s.x + s.w, s.y + s.h)
        else:
            r = QRectF(s.x, s.y, s.w, s.h).normalized()
            p.drawRect(r)
        # carrés bleus
        p.setBrush(QBrush(QColor("#00A2FF")))
        p.setPen(Qt.PenStyle.NoPen)
        for r in self._handles_for(s):
            p.drawRect(r)
        p.restore()


# ------------------ OUTIL RECT ------------------
class RectTool(Tool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._start: Optional[QPointF] = None
        self._preview_rect: Optional[QRectF] = None

    def on_mouse_press(self, pos, ev):
        self._start = QPointF(pos)
        self._preview_rect = QRectF(self._start, self._start)
        self.canvas.update()

    def on_mouse_move(self, pos, ev):
        if not self._start:
            return
        r = QRectF(self._start, pos)
        # Shift → carré
        if ev.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            side = min(abs(r.width()), abs(r.height()))
            r.setWidth(side if r.width() >= 0 else -side)
            r.setHeight(side if r.height() >= 0 else -side)
        self._preview_rect = r
        self.canvas.update()

    def on_mouse_release(self, pos, ev):
        if not self._start:
            return
        r = self._preview_rect.normalized()
        shape = RectShape(r.x(), r.y(), r.width(), r.height(),
                          stroke_color="#000000", fill_color="#FFFFFF", stroke_width=2)
        self.canvas.doc.add_shape(shape)
        self._start = None
        self._preview_rect = None
        self.canvas.update()

    def draw_overlay(self, p):
        if not self._preview_rect:
            return
        p.save()
        p.setPen(QPen(QColor("#0077FF"), 1, Qt.PenStyle.DashLine))
        p.setBrush(QBrush(QColor(0, 119, 255, 30)))
        p.drawRect(self._preview_rect)
        p.restore()


# ------------------ OUTIL ELLIPSE ------------------
class EllipseTool(RectTool):
    """Même logique que RectTool mais création d'ellipse à la fin."""
    def on_mouse_release(self, pos, ev):
        if not self._start:
            return
        r = self._preview_rect.normalized()
        shape = EllipseShape(r.x(), r.y(), r.width(), r.height(),
                             stroke_color="#000000", fill_color="#FFFFFF", stroke_width=2)
        self.canvas.doc.add_shape(shape)
        self._start = None
        self._preview_rect = None
        self.canvas.update()

    def draw_overlay(self, p):
        if not self._preview_rect:
            return
        p.save()
        p.setPen(QPen(QColor("#00AA55"), 1, Qt.PenStyle.DashLine))
        p.setBrush(QBrush(QColor(0, 170, 85, 30)))
        p.drawEllipse(self._preview_rect)
        p.restore()


# ------------------ OUTIL LIGNE ------------------
class LineTool(Tool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._start: Optional[QPointF] = None
        self._current: Optional[QPointF] = None

    def on_mouse_press(self, pos, ev):
        self._start = QPointF(pos)
        self._current = QPointF(pos)
        self.canvas.update()

    def on_mouse_move(self, pos, ev):
        if not self._start:
            return
        x, y = pos.x(), pos.y()
        # Option : contraindre avec Shift à horizontale/verticale
        if ev.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            dx = abs(x - self._start.x())
            dy = abs(y - self._start.y())
            if dx > dy:
                pos = QPointF(x, self._start.y())
            else:
                pos = QPointF(self._start.x(), y)
        self._current = QPointF(pos)
        self.canvas.update()

    def on_mouse_release(self, pos, ev):
        if not self._start:
            return
        end = QPointF(self._current)
        shape = LineShape(self._start.x(), self._start.y(),
                          end.x() - self._start.x(), end.y() - self._start.y(),
                          stroke_color="#000000", stroke_width=2, fill_color="")
        self.canvas.doc.add_shape(shape)
        self._start = None
        self._current = None
        self.canvas.update()

    def draw_overlay(self, p):
        if self._start and self._current:
            p.save()
            p.setPen(QPen(QColor("#AA00FF"), 1, Qt.PenStyle.DashLine))
            p.drawLine(self._start, self._current)
            p.restore()
