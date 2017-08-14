# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bb_downloader_download.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DownloadDialog(object):
    def __init__(self, fileTree, account):
        self.fileTree = fileTree
        print(fileTree)
        self.account = account

    def setupUi(self, DownloadDialog):
        DownloadDialog.setObjectName("DownloadDialog")
        DownloadDialog.setFixedSize(475, 248)
        self.DownloadDialog = DownloadDialog

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("bb_favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DownloadDialog.setWindowIcon(icon)
        
        self.CurrentDownloadBar = QtWidgets.QProgressBar(DownloadDialog)
        self.CurrentDownloadBar.setGeometry(QtCore.QRect(46, 88, 401, 23))
        self.CurrentDownloadBar.setProperty("value", 0)
        self.CurrentDownloadBar.setObjectName("CurrentDownloadBar")
        
        self.TotalDownloadBar = QtWidgets.QProgressBar(DownloadDialog)
        self.TotalDownloadBar.setGeometry(QtCore.QRect(46, 148, 401, 23))
        self.TotalDownloadBar.setProperty("value", 0)
        self.TotalDownloadBar.setObjectName("TotalDownloadBar")
        self.TotalDownloadLabel = QtWidgets.QLabel(DownloadDialog)
        self.TotalDownloadLabel.setGeometry(QtCore.QRect(46, 128, 161, 16))
        
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)

        self.TotalDownloadLabel.setFont(font)
        self.TotalDownloadLabel.setObjectName("TotalDownloadLabel")
        self.CurrentDownloadLabel = QtWidgets.QLabel(DownloadDialog)
        self.CurrentDownloadLabel.setGeometry(QtCore.QRect(46, 68, 161, 16))
        self.CurrentDownloadLabel.setFont(font)
        self.CurrentDownloadLabel.setObjectName("CurrentDownloadLabel")

        self.DownloadCancelButton = QtWidgets.QPushButton(DownloadDialog)
        self.DownloadCancelButton.setGeometry(QtCore.QRect(350, 200, 101, 31))
        self.DownloadCancelButton.clicked.connect(self.DownloadDialog.close)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DownloadCancelButton.sizePolicy().hasHeightForWidth())
        self.DownloadCancelButton.setSizePolicy(sizePolicy)

        self.DownloadCancelButton.setObjectName("DownloadCancelButton")
        self.DownloadTitle = QtWidgets.QLabel(DownloadDialog)
        self.DownloadTitle.setGeometry(QtCore.QRect(30, 20, 211, 31))

        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.DownloadTitle.setFont(font)
        self.DownloadTitle.setObjectName("DownloadTitle")

        self.retranslateUi(DownloadDialog)
        QtCore.QMetaObject.connectSlotsByName(DownloadDialog)

    def retranslateUi(self, DownloadDialog):
        _translate = QtCore.QCoreApplication.translate
        DownloadDialog.setWindowTitle(_translate("DownloadDialog", "Downloading..."))
        self.TotalDownloadLabel.setText(_translate("DownloadDialog", "전체 다운로드 진행률"))
        self.CurrentDownloadLabel.setText(_translate("DownloadDialog", "개별 다운로드 진행률"))
        self.DownloadCancelButton.setText(_translate("DownloadDialog", "다운로드 취소"))
        self.DownloadTitle.setText(_translate("DownloadDialog", "다운로드 중입니다..."))