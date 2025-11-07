"""
Point d'entrée de l'application.
Crée l'application Qt, instancie la MainWindow et lance la boucle d'événements.
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # QApplication = moteur d'événements Qt (nécessaire à tous les widgets)
    app = QApplication(sys.argv)

    # Notre fenêtre principale
    w = MainWindow()
    w.show()

    # Boucle d'événements (bloquante jusqu'à fermeture)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
