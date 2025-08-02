# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CNMapViewer.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(400, 400)
        MainWindow.setMinimumSize(QSize(400, 400))
        self.action_New = QAction(MainWindow)
        self.action_New.setObjectName(u"action_New")
        self.actionaboutQt = QAction(MainWindow)
        self.actionaboutQt.setObjectName(u"actionaboutQt")
        self.actionTEST = QAction(MainWindow)
        self.actionTEST.setObjectName(u"actionTEST")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 80, 128, 128))
        self.label.setPixmap(QPixmap(u":/assets/icons/add.ico"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 400, 22))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_Edit = QMenu(self.menubar)
        self.menu_Edit.setObjectName(u"menu_Edit")
        self.menu_About = QMenu(self.menubar)
        self.menu_About.setObjectName(u"menu_About")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_About.menuAction())
        self.menu_File.addAction(self.action_New)
        self.menu_Edit.addAction(self.actionTEST)
        self.menu_About.addAction(self.actionaboutQt)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_New.setText(QCoreApplication.translate("MainWindow", u"&New", None))
        self.actionaboutQt.setText(QCoreApplication.translate("MainWindow", u"aboutQt", None))
        self.actionTEST.setText(QCoreApplication.translate("MainWindow", u"TEST", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Edit.setTitle(QCoreApplication.translate("MainWindow", u"&Edit", None))
        self.menu_About.setTitle(QCoreApplication.translate("MainWindow", u"&About", None))
    # retranslateUi
