import sys
import queue  # for pyinstaller
import requests
from PyQt5 import QtWidgets

# Ui modules
import bb_downloader_mainUi as mainUi
import bb_downloader_loginUi as loginUi
import bb_downloader_downloadUi as downloadUi

# fuction module
import bb_downloader_func as myfunc

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = QtWidgets.QMainWindow()
    ui = loginUi.Ui_LoginWindow()
    ui.setupUi(LoginWindow)
    LoginWindow.show()
    sys.exit(app.exec_())