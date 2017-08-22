# bb_downloader_downloadUi.py

from PyQt5 import QtCore, QtGui, QtWidgets
import bb_downloader_func as myfunc

class Worker(QtCore.QThread):
    signal = QtCore.pyqtSignal(int, int, int)
    def __init__(self, ui, parent=None):
        super(Worker, self).__init__()
        self.ui = ui

    def run(self):
        self.ui.downloadFiles(self.signal)
        self.signal.emit(-1, -1, -1)  # set wellDone True

class Ui_DownloadDialog(object):
    CurrentDownloadBar = 0
    TotalDownloadBar = 0
    wellDone = False

    def __init__(self, DownloadDialog, file_list, account):
        self.file_list = file_list
        self.account = account
        self.total_size = 0
        self.DownloadDialog = DownloadDialog
        for myfile in file_list:
            if isinstance(myfile, myfunc.Menu):
                continue
            self.total_size += int(myfile.size)

    def start(self):
        self.thread = Worker(self)
        self.thread.signal.connect(self.setRange)
        self.thread.start()
        self.thread.finished.connect(self.downloadFinished)

    def downloadFinished(self):
        if Ui_DownloadDialog.wellDone:
            NotifyWindow = QtWidgets.QMessageBox(self.DownloadDialog)
            NotifyWindow.setWindowTitle("다운로드 성공!")
            NotifyWindow.setText("다운로드를 전부 완료했습니다.")
            NotifyWindow.setStandardButtons(QtWidgets.QMessageBox.Ok)
            NotifyWindow.setIcon(QtWidgets.QMessageBox.Information)
            NotifyWindow.show()
            Ui_DownloadDialog.wellDone = False
            self.DownloadDialog.close()

    @classmethod
    def setRange(cls, current_maximum, current_value, total_value):
        if current_maximum == -1 and current_value == -1 and total_value == -1:
            cls.wellDone = True
            return

        cls.CurrentDownloadBar.setMaximum(current_maximum)
        cls.CurrentDownloadBar.setValue(current_value)
        cls.TotalDownloadBar.setValue(total_value)

    def setupUi(self, DownloadDialog):
        DownloadDialog.setObjectName("DownloadDialog")
        DownloadDialog.setFixedSize(475, 248)
        self.DownloadDialog = DownloadDialog

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("bb_favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DownloadDialog.setWindowIcon(icon)

        Ui_DownloadDialog.CurrentDownloadBar = QtWidgets.QProgressBar(DownloadDialog)
        Ui_DownloadDialog.CurrentDownloadBar.setGeometry(QtCore.QRect(46, 88, 401, 23))
        Ui_DownloadDialog.CurrentDownloadBar.setProperty("value", 0)
        Ui_DownloadDialog.CurrentDownloadBar.setObjectName("CurrentDownloadBar")

        Ui_DownloadDialog.TotalDownloadBar = QtWidgets.QProgressBar(DownloadDialog)
        Ui_DownloadDialog.TotalDownloadBar.setGeometry(QtCore.QRect(46, 148, 401, 23))
        Ui_DownloadDialog.TotalDownloadBar.setProperty("value", 0)
        Ui_DownloadDialog.TotalDownloadBar.setObjectName("TotalDownloadBar")
        Ui_DownloadDialog.TotalDownloadBar.setMaximum(self.total_size)

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
        self.DownloadCancelButton.clicked.connect(self.downloadQuit)

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

        self.start()

    def retranslateUi(self, DownloadDialog):
        _translate = QtCore.QCoreApplication.translate
        DownloadDialog.setWindowTitle(_translate("DownloadDialog", "Downloading..."))
        self.TotalDownloadLabel.setText(_translate("DownloadDialog", "전체 다운로드 진행률"))
        self.CurrentDownloadLabel.setText(_translate("DownloadDialog", "개별 다운로드 진행률"))
        self.DownloadCancelButton.setText(_translate("DownloadDialog", "다운로드 취소"))
        self.DownloadTitle.setText(_translate("DownloadDialog", "다운로드 중입니다..."))

    def downloadFiles(self, signal):
        for myfile in self.file_list:
            if isinstance(myfile, myfunc.Menu):
                myfile.savePage()
            else:
                myfile.saveFile(self, signal)

    def downloadQuit(self):
        self.thread.terminate()
        self.DownloadDialog.close()