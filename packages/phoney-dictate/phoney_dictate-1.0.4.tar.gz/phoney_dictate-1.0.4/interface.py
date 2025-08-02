# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.copyButton = QtWidgets.QPushButton(self.centralwidget)
        self.copyButton.setMinimumSize(QtCore.QSize(0, 45))
        icon = QtGui.QIcon.fromTheme("gtk-copy")
        self.copyButton.setIcon(icon)
        self.copyButton.setIconSize(QtCore.QSize(24, 24))
        self.copyButton.setFlat(False)
        self.copyButton.setObjectName("copyButton")
        self.verticalLayout.addWidget(self.copyButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnSmaller = QtWidgets.QPushButton(self.centralwidget)
        self.btnSmaller.setMaximumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.btnSmaller.setFont(font)
        self.btnSmaller.setFlat(False)
        self.btnSmaller.setObjectName("btnSmaller")
        self.horizontalLayout_2.addWidget(self.btnSmaller)
        self.btnLarger = QtWidgets.QPushButton(self.centralwidget)
        self.btnLarger.setMaximumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.btnLarger.setFont(font)
        self.btnLarger.setFlat(False)
        self.btnLarger.setObjectName("btnLarger")
        self.horizontalLayout_2.addWidget(self.btnLarger)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.linkLabel = QtWidgets.QLabel(self.centralwidget)
        self.linkLabel.setText("")
        self.linkLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.linkLabel.setObjectName("linkLabel")
        self.verticalLayout.addWidget(self.linkLabel)
        self.iconLabel = QtWidgets.QLabel(self.centralwidget)
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.iconLabel.setObjectName("iconLabel")
        self.verticalLayout.addWidget(self.iconLabel)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.textBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.textBox.setFont(font)
        self.textBox.setPlainText("")
        self.textBox.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.textBox.setObjectName("textBox")
        self.horizontalLayout.addWidget(self.textBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btnSmaller.clicked.connect(self.textBox.zoomOut)
        self.btnLarger.clicked.connect(self.textBox.zoomIn)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.copyButton.setToolTip(_translate("MainWindow", "Copy all text to the clipboard"))
        self.copyButton.setText(_translate("MainWindow", "&Copy"))
        self.btnSmaller.setToolTip(_translate("MainWindow", "Make font size smaller"))
        self.btnSmaller.setText(_translate("MainWindow", "-"))
        self.btnLarger.setToolTip(_translate("MainWindow", "Make font size larger"))
        self.btnLarger.setText(_translate("MainWindow", "+"))
