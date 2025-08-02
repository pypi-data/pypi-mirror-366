from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


def main() -> None:
    app = QApplication([])

    win = QWidget()

    layout = QVBoxLayout()
    label = QLabel("Hello, PyQt5!")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    btn = QPushButton(text="PUSH ME")
    layout.addWidget(btn)

    win.setLayout(layout)
    win.resize(400, 300)

    btn.clicked.connect(
        lambda: [
            print("exit"),  # noqa: T201
            win.close(),
        ],
    )

    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
