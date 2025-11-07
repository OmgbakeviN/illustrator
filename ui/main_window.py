"""
Fenêtre principale.
- Barre de menus : Fichier (Nouveau/Ouvrir/Enregistrer), Édition (Undo/Redo), Vue (2D/3D).
- Onglets : pour l'instant un onglet 2D, un placeholder 3D viendra plus tard.
- Gère un Document en mémoire et passe la référence au Canvas2D.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QTabWidget, QWidget, QVBoxLayout, QMessageBox
)
from PyQt6.QtGui import QIcon, QKeySequence
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

        # --- Modèle & pile de commandes ---
        self.doc = Document()
        self.commands = CommandStack()

        # --- Zone centrale : onglets (2D / 3D plus tard) ---
        self.tabs = QTabWidget()
        self.canvas2d = Canvas2D(self.doc, self)
        self.tabs.addTab(self.canvas2d, "2D")

        # Placeholder 3D désactivé pour le moment (à l'étape 6)
        # self.canvas3d = Canvas3D(self.doc, self)
        # self.tabs.addTab(self.canvas3d, "3D")

        self.setCentralWidget(self.tabs)

        # Barre de statut (texte en bas)
        self.statusBar().showMessage("Prêt")

        # Construire les menus et leurs actions
        self._build_menus()

        # Mettre à jour l'état des actions Undo/Redo (désactivées au départ)
        self._refresh_edit_actions()

    # ----------------- Menus -----------------
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

        # Pour l’instant, simple placeholder pour basculer 2D/3D
        # On activera l’onglet 3D quand il existera.
        a_go_2d = m_view.addAction("Basculer vers 2D")
        a_go_2d.triggered.connect(lambda: self.tabs.setCurrentIndex(0))

        # Exemple si l’onglet 3D était présent :
        # a_go_3d = m_view.addAction("Basculer vers 3D")
        # a_go_3d.triggered.connect(lambda: self.tabs.setCurrentIndex(1))

    # ----------------- Actions Fichier -----------------
    def on_new(self):
        """Réinitialise le document courant et rafraîchit le canvas."""
        self.doc.clear()
        self.canvas2d.set_document(self.doc)
        self.statusBar().showMessage("Nouveau document")

    def on_open(self):
        """Ouvre un .json et remplace le document courant."""
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
        """Sauvegarde rapide : si pas de chemin connu, bascule sur 'Enregistrer sous'."""
        # À l'étape 0, on ne garde pas encore l'état du 'dernier chemin'.
        # On passe donc systématiquement par 'Enregistrer sous'.
        self.on_save_as()

    def on_save_as(self):
        """Demande un chemin et sauvegarde le document JSON."""
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

    # ----------------- Actions Édition -----------------
    def _refresh_edit_actions(self):
        """Active/désactive Undo/Redo selon l'état de la pile."""
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
