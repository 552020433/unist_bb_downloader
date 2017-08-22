# bb_downloader_loginUi.py

from PyQt5 import QtCore, QtGui, QtWidgets
import bb_downloader_func as myfunc
import bb_downloader_mainUi as mainUi

class Worker(QtCore.QThread):
    def __init__(self, account):
        super(Worker, self).__init__()
        self.account = account

    def run(self):
        self.account.getCourseList()

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.setFixedSize(323, 227)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("bb_favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LoginWindow.setWindowIcon(icon)
        self.LoginWindow = LoginWindow

        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.IDEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.IDEdit.setGeometry(QtCore.QRect(120, 80, 113, 20))
        self.IDEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.IDEdit.setObjectName("IDEdit")

        self.PasswdEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.PasswdEdit.setGeometry(QtCore.QRect(120, 120, 113, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PasswdEdit.sizePolicy().hasHeightForWidth())
        self.PasswdEdit.setSizePolicy(sizePolicy)
        self.PasswdEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.PasswdEdit.setObjectName("PasswdEdit")

        self.IDLabel = QtWidgets.QLabel(self.centralwidget)
        self.IDLabel.setGeometry(QtCore.QRect(80, 80, 41, 21))
        self.IDLabel.setObjectName("IDLabel")
        self.PasswdLabel = QtWidgets.QLabel(self.centralwidget)
        self.PasswdLabel.setGeometry(QtCore.QRect(60, 120, 51, 20))
        self.PasswdLabel.setObjectName("PasswdLabel")
        self.TitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.TitleLabel.setGeometry(QtCore.QRect(70, 30, 191, 21))

        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)

        self.TitleLabel.setFont(font)
        self.TitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.TitleLabel.setObjectName("TitleLabel")

        self.LoginButton = QtWidgets.QPushButton(self.centralwidget)
        self.LoginButton.setGeometry(QtCore.QRect(60, 170, 91, 31))
        self.LoginButton.setObjectName("LoginButton")
        self.LoginButton.clicked.connect(self.tryLogin)

        self.ExitButton = QtWidgets.QPushButton(self.centralwidget)
        self.ExitButton.setGeometry(QtCore.QRect(170, 170, 91, 31))
        self.ExitButton.setObjectName("ExitButton")
        self.ExitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)

        self.PasswdEdit.returnPressed.connect(self.tryLogin)

        LoginWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "BB Downloader Login"))
        self.IDLabel.setText(_translate("LoginWindow", "학번: "))
        self.PasswdLabel.setText(_translate("LoginWindow", "비밀번호:"))
        self.TitleLabel.setText(_translate("LoginWindow", "BB 다운로더 v1.0"))
        self.LoginButton.setText(_translate("LoginWindow", "로그인"))
        self.ExitButton.setText(_translate("LoginWindow", "나가기"))

    def tryLogin(self):
        self.LoginWindow.setEnabled(False)
        self.LoginWindow.repaint()

        student_id = self.IDEdit.text()
        pw = self.PasswdEdit.text()

        try:
            self.account = myfunc.Account(student_id, pw)
        except myfunc.LoginFail:
            msg = QtWidgets.QMessageBox(self.LoginWindow)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("로그인에 실패했습니다.\n\n학번과 비밀번호를 다시 확인해주세요..")
            msg.setWindowTitle("로그인 실패..")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()

            self.PasswdEdit.clear()
            self.LoginWindow.setEnabled(True)
            return

        self.WaitingWindow = QtWidgets.QMessageBox(self.LoginWindow)
        self.WaitingWindow.setWindowTitle("과목 목록 불러오는 중..")
        self.WaitingWindow.setText("과목 목록을 불러오는 중입니다.\n잠시만 기다려주세요...\n(시간이 1분 정도 걸립니다)")
        self.WaitingWindow.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        self.WaitingWindow.button(QtWidgets.QMessageBox.Cancel).clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.WaitingWindow.setIcon(QtWidgets.QMessageBox.Information)
        self.WaitingWindow.show()

        self.thread = Worker(self.account)
        self.thread.start()
        self.thread.finished.connect(self.end)

    def end(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = mainUi.Ui_MainWindow()
        self.ui.setupUi(self.MainWindow, self.account)
        self.MainWindow.show()
        self.WaitingWindow.accept()
        NotifyWindow = QtWidgets.QMessageBox(self.MainWindow)
        NotifyWindow.setWindowTitle("로딩 성공!")
        NotifyWindow.setText("로딩을 전부 완료했습니다.")
        NotifyWindow.setStandardButtons(QtWidgets.QMessageBox.Ok)
        NotifyWindow.setIcon(QtWidgets.QMessageBox.Information)
        NotifyWindow.show()
        self.LoginWindow.close()