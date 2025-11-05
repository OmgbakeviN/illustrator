import sys
import random
from PyQt6 import QtWidgets, QtGui, QtCore

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hello", "Bonjour", "Ciao", "Hola", "Ciao"]

        self.button = QtWidgets.QPushButton("Click Me")
        self.text = QtWidgets.QLabel("Hello", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.changeText)

    def changeText(self):
        self.text.setText(random.choice(self.hello))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWidget()
    widget.show()

    sys.exit(app.exec())
