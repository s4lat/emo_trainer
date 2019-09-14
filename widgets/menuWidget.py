# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'templates_ui/menu.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MenuWidget(QWidget):
    def __init__(self, parent=None):
        super(MenuWidget, self).__init__(parent)

        self.setupUi(self);

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(403, 453)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMouseTracking(False)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.label = QLabel(Form)
        self.label.setMinimumSize(QSize(250, 50))
        self.label.setMaximumSize(QSize(200, 64))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 1, 1, 1)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 1, 1, 1)
        spacerItem3 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 2, 2, 1, 1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.testBtn = QPushButton(Form)
        self.testBtn.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.testBtn.sizePolicy().hasHeightForWidth())
        self.testBtn.setSizePolicy(sizePolicy)
        self.testBtn.setMinimumSize(QSize(250, 50))
        self.testBtn.setMaximumSize(QSize(250, 50))
        font = QFont()
        font.setPointSize(16)
        self.testBtn.setFont(font)
        self.testBtn.setObjectName("testBtn")
        self.verticalLayout.addWidget(self.testBtn)
        self.trainBtn = QPushButton(Form)
        self.trainBtn.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.trainBtn.sizePolicy().hasHeightForWidth())
        self.trainBtn.setSizePolicy(sizePolicy)
        self.trainBtn.setMinimumSize(QSize(250, 50))
        self.trainBtn.setMaximumSize(QSize(250, 50))
        font = QFont()
        font.setPointSize(16)
        self.trainBtn.setFont(font)
        self.trainBtn.setObjectName("trainBtn")
        self.verticalLayout.addWidget(self.trainBtn)
        self.abotBtn = QPushButton(Form)
        self.abotBtn.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abotBtn.sizePolicy().hasHeightForWidth())
        self.abotBtn.setSizePolicy(sizePolicy)
        self.abotBtn.setMinimumSize(QSize(250, 50))
        self.abotBtn.setMaximumSize(QSize(250, 50))
        font = QFont()
        font.setPointSize(16)
        self.abotBtn.setFont(font)
        self.abotBtn.setObjectName("abotBtn")
        self.verticalLayout.addWidget(self.abotBtn)
        self.exitBtn = QPushButton(Form)
        self.exitBtn.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exitBtn.sizePolicy().hasHeightForWidth())
        self.exitBtn.setSizePolicy(sizePolicy)
        self.exitBtn.setMinimumSize(QSize(250, 50))
        self.exitBtn.setMaximumSize(QSize(250, 50))
        font = QFont()
        font.setPointSize(16)
        self.exitBtn.setFont(font)
        self.exitBtn.setObjectName("exitBtn")
        self.verticalLayout.addWidget(self.exitBtn)
        self.gridLayout.addLayout(self.verticalLayout, 2, 1, 1, 1)
        spacerItem4 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 2, 0, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:24pt;\">EmoTrainer</span></p></body></html>"))
        self.testBtn.setText(_translate("Form", "Тестирование"))
        self.trainBtn.setText(_translate("Form", "Упражнения"))
        self.abotBtn.setText(_translate("Form", "О программе"))
        self.exitBtn.setText(_translate("Form", "Выйти"))




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = MenuWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())