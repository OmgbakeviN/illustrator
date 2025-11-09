"""
Fenêtre principale complète (Menus + Toolbar + Zoom)
Étape 2 finalisée.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QTabWidget, QMessageBox, QToolBar
)
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtCore import Qt

from core.document import Document
from core.io_json import save_document, load_document
from core.commands import CommandStack
from ui.init_2d import Canvas2D


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini-Illustrator")
        self.resize(1280, 800)

        # Modèle
        self.doc = Document()
        self.commands = CommandStack()

        # Canvas 2D
        self.tabs = QTabWidget()
        self.canvas2d = Canvas2D(self.doc, self)
        self.tabs.addTab(self.canvas2d, "2D")
        self.setCentralWidget(self.tabs)

        # Barre de statut
        self.statusBar().showMessage("Prêt")

        # Menus et Toolbar
        self._build_menus()
        self._build_toolbar()

        self._refresh_edit_actions()

    # ------------------------------------------------------------------
    # MENU FICHIER / ÉDITION / VUE
    # ------------------------------------------------------------------
    def _build_menus(self):
        # --- MENU FICHIER ---
        m_file = self.menuBar().addMenu("&Fichier")

        a_new = m_file.addAction("Nouveau")
        a_new.setShortcut(QKeySequence.StandardKey.New)
        a_new.triggered.connect(self.on_new)

        a_open = m_file.addAction("Ouvrir…")
        a_open.setShortcut(QKeySequence.StandardKey.Open)
        a_open.triggered.connect(self.on_open)

        a_save = m_file.addAction("Enregistrer")
        a_save.setShortcut(QKeySequence.StandardKey.Save)
        a_save.triggered.connect(self.on_save)

        a_save_as = m_file.addAction("Enregistrer sous…")
        a_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        a_save_as.triggered.connect(self.on_save_as)

        # --- MENU ÉDITION ---
        m_edit = self.menuBar().addMenu("&Édition")

        self.a_undo = m_edit.addAction("Annuler")
        self.a_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.a_undo.triggered.connect(self.on_undo)

        self.a_redo = m_edit.addAction("Rétablir")
        self.a_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.a_redo.triggered.connect(self.on_redo)

        # --- MENU VUE ---
        m_view = self.menuBar().addMenu("&Vue")

        a_go_2d = m_view.addAction("Basculer vers 2D")
        a_go_2d.triggered.connect(lambda: self.tabs.setCurrentIndex(0))

    # ------------------------------------------------------------------
    # TOOLBAR (Étape 2)
    # ------------------------------------------------------------------
    def _build_toolbar(self):
        tb = QToolBar("Outils", self)
        tb.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        act_select = QAction("Select", self)
        act_select.triggered.connect(lambda: self.canvas2d.set_tool("select"))

        act_rect = QAction("Rect", self)
        act_rect.triggered.connect(lambda: self.canvas2d.set_tool("rect"))

        act_ellipse = QAction("Ellipse", self)
        act_ellipse.triggered.connect(lambda: self.canvas2d.set_tool("ellipse"))

        act_line = QAction("Ligne", self)
        act_line.triggered.connect(lambda: self.canvas2d.set_tool("line"))

        tb.addAction(act_select)
        tb.addAction(act_rect)
        tb.addAction(act_ellipse)
        tb.addAction(act_line)
        tb.addSeparator()

        act_zoom_in = QAction("Zoom +", self)
        act_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        act_zoom_out = QAction("Zoom -", self)
        act_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        act_zoom_reset = QAction("Reset", self)

        act_zoom_in.triggered.connect(self.canvas2d.zoom_in)
        act_zoom_out.triggered.connect(self.canvas2d.zoom_out)
        act_zoom_reset.triggered.connect(self.canvas2d.zoom_reset)

        tb.addAction(act_zoom_in)
        tb.addAction(act_zoom_out)
        tb.addAction(act_zoom_reset)

    # ------------------------------------------------------------------
    # LOGIQUE FICHIER
    # ------------------------------------------------------------------
    def on_new(self):
        self.doc.clear()
        self.canvas2d.set_document(self.doc)
        self.statusBar().showMessage("Nouveau document")

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir", filter="Projet Mini-Illustrator (*.json)"
        )
        if not path:
            return
        try:
            self.doc = load_document(path)
            self.canvas2d.set_document(self.doc)
            self.statusBar().showMessage(f"Ouvert : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'ouverture", str(e))

    def on_save(self):
        self.on_save_as()  # version simplifiée

    def on_save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", filter="Projet Mini-Illustrator (*.json)"
        )
        if not path:
            return
        try:
            save_document(self.doc, path)
            self.statusBar().showMessage(f"Enregistré : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'enregistrement", str(e))

    # ------------------------------------------------------------------
    # ANNULER / RÉTABLIR
    # ------------------------------------------------------------------
    def _refresh_edit_actions(self):
        self.a_undo.setEnabled(self.commands.can_undo())
        self.a_redo.setEnabled(self.commands.can_redo())

    def on_undo(self):
        self.commands.undo()
        self._refresh_edit_actions()
        self.canvas2d.update()
        self.statusBar().showMessage("Annuler")

    def on_redo(self):
        self.commands.redo()
        self._refresh_edit_actions()
        self.canvas2d.update()
        self.statusBar().showMessage("Rétablir")
