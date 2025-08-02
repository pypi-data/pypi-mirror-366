from PySide2.QtGui import QFont
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QMessageBox

from ex04_pyside2.depends.ui_CNMapViewer import Ui_MainWindow


class CNMapViewer(QMainWindow, Ui_MainWindow):
    """主窗口."""

    def __init__(self) -> None:
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle("CNMap Ver1.0")
        self.resize(800, 600)
        self.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))

        pixmap = QPixmap(":/assets/icons/add.ico")
        self.label.setPixmap(pixmap)
        self.actionaboutQt.triggered.connect(self.on_about)

    def on_about(self) -> None:
        QMessageBox.aboutQt(self, title="example for qt")
