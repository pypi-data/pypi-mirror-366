from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget

from ex04_pyside2.depends.CNMapViewer import CNMapViewer


def main() -> None:
    app = QApplication([])

    win = QWidget()
    win.setWindowTitle("pyside2 simple gui")
    win.setWindowIcon(QIcon(":/assets/icons/remove.ico"))

    layout = QVBoxLayout()
    viewer = CNMapViewer()
    layout.addWidget(viewer)
    label = QLabel("Hello, Pyside2!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    btn = QPushButton(text="PUSH ME")
    layout.addWidget(btn)

    win.setLayout(layout)
    win.resize(400, 300)

    btn.clicked.connect(
        lambda: [
            print("exit"),
            win.close(),
        ],
    )

    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
