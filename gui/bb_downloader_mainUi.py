from PyQt5 import QtCore, QtGui, QtWidgets
import bb_downloader_func as myfunc
import bb_downloader_downloadUi as downloadUi

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, account):
        MainWindow.setObjectName('MainWindow')
        MainWindow.setFixedSize(782, 465)
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)
        MainWindow.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('bb_favicon.ico'), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)

        self.account = account
        self.MainWindow = MainWindow
        self.download_list = []

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        self.downloadButton = QtWidgets.QPushButton(self.centralwidget)
        self.downloadButton.setGeometry(QtCore.QRect(520, 380, 101, 41))
        self.downloadButton.setObjectName('downloadButton')
        self.downloadButton.clicked.connect(self.Download)

        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(640, 380, 101, 41))
        self.quitButton.setObjectName('quitButton')
        self.quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)

        self.courseTreeTitle = QtWidgets.QLabel(self.centralwidget)
        self.courseTreeTitle.setGeometry(QtCore.QRect(40, 20, 231, 21))

        font = QtGui.QFont()
        font.setFamily('맑은 고딕')
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)

        self.courseTreeTitle.setFont(font)
        self.courseTreeTitle.setObjectName('courseTreeTitle')
        self.fileTreeTitle = QtWidgets.QLabel(self.centralwidget)
        self.fileTreeTitle.setGeometry(QtCore.QRect(330, 20, 231, 21))

        self.fileTreeTitle.setFont(font)
        self.fileTreeTitle.setObjectName('fileTreeTitle')
        self.fileTree = QtWidgets.QTreeWidget(self.centralwidget)
        self.fileTree.setGeometry(QtCore.QRect(330, 50, 411, 321))
        self.fileTree.setObjectName('fileTree')
        self.fileTree.setColumnCount(2)
        self.fileTree.header().resizeSection(0, 300)
        self.fileTree.itemChanged.connect(self.handleFileChange)

        self.courseTree = QtWidgets.QTreeWidget(self.centralwidget)
        self.courseTree.setGeometry(QtCore.QRect(40, 50, 256, 321))
        self.courseTree.setObjectName('courseTree')
        self.courseTree.itemChanged.connect(self.handleCourseChange)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 782, 21))
        self.menubar.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menubar.setAcceptDrops(False)
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName('menubar')

        self.menubar.addAction("로그아웃", self.Logout)
        self.menubar.addAction("현재 폴더 열기", self.OpenFolder)
        self.menubar.addAction("프로그램 정보", self.ProgramAbout)

        MainWindow.setMenuBar(self.menubar)

        self.LoadTreeItems()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)        


    def Download(self):
        import bb_downloader_downloadUi as downloadUi
        DownloadDialog = QtWidgets.QDialog(self.MainWindow)
        ui = downloadUi.Ui_DownloadDialog(self.download_list, self.account)
        ui.setupUi(DownloadDialog)
        DownloadDialog.exec_()

    def Logout(self):
        import bb_downloader_loginUi as loginUi
        self.MainWindow.close()
        self.LoginWindow = QtWidgets.QMainWindow()
        self.ui = loginUi.Ui_LoginWindow()
        self.ui.setupUi(self.LoginWindow)
        self.LoginWindow.show()

    def OpenFolder(self):
        import subprocess
        subprocess.Popen(r'explorer "."')

    def ProgramAbout(self):
        AboutWindow = QtWidgets.QMessageBox(self.MainWindow)
        AboutWindow.setWindowTitle("BB Downloader 정보")
        AboutWindow.setText('버전: 1.0<br>라이센스: GPL v3.0<br>이메일: kcm4482@unist.ac.kr<br>Github: \
        <a href ="https://github.com/kcm4482/unist_bb_downloader">https://github.com/kcm4482/unist_bb_downloader</a>')
        AboutWindow.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse)
        AboutWindow.setStandardButtons(QtWidgets.QMessageBox.Ok)
        AboutWindow.setIcon(QtWidgets.QMessageBox.Information)
        AboutWindow.setTextFormat(QtCore.Qt.RichText)
        AboutWindow.exec_()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', 'BB Downloader v1.0'))
        self.downloadButton.setText(_translate('MainWindow', '다운로드!'))
        self.quitButton.setText(_translate('MainWindow', '나가기'))
        self.courseTreeTitle.setText(_translate('MainWindow', '다운로드 가능한 과목'))
        self.fileTreeTitle.setText(_translate('MainWindow', '다운로드 가능한 항목'))
        self.fileTree.headerItem().setText(0, _translate('MainWindow', '항목'))
        self.fileTree.headerItem().setText(1, _translate('MainWindow', '파일 크기'))
        _Ui_MainWindow__sortingEnabled = self.fileTree.isSortingEnabled()
        self.fileTree.setSortingEnabled(False)
        self.fileTree.setSortingEnabled(_Ui_MainWindow__sortingEnabled)
        self.courseTree.headerItem().setText(0, _translate('MainWindow', '과목'))
        _Ui_MainWindow__sortingEnabled = self.courseTree.isSortingEnabled()
        self.courseTree.setSortingEnabled(False)
        self.courseTree.setSortingEnabled(_Ui_MainWindow__sortingEnabled)

    def LoadTreeItems(self):
        self.total_item = QtWidgets.QTreeWidgetItem(self.courseTree)
        self.total_item.setFlags(self.total_item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
        self.total_item.setText(0, '전체선택')
        self.total_item.setCheckState(0, QtCore.Qt.Unchecked)
        self.total_item.setExpanded(True)
        for course in self.account.course_list:
            item = QtWidgets.QTreeWidgetItem(self.total_item)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setText(0, course.name)
            item.setCheckState(0, QtCore.Qt.Unchecked)

    def handleCourseChange(self, item, column):
        if item == self.total_item:
            return
        if item.checkState(column) == QtCore.Qt.Checked:
            l = self.fileTree.findItems(item.text(0), QtCore.Qt.MatchExactly)
            if l == []:
                for _course in self.account.course_list:
                    if _course.name == item.text(0):
                        course = _course
                        break

                course_item = QtWidgets.QTreeWidgetItem(self.fileTree)
                course_item.setFlags(item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                course_item.setText(0, course.name)
                size = self.getSizeUnit(course.size)
                course_item.setText(1, size)
                course_item.setCheckState(0, QtCore.Qt.Checked)
                course_item.setExpanded(True)
                for menu in course:
                    menu_item = QtWidgets.QTreeWidgetItem(course_item)
                    menu_item.setFlags(menu_item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                    menu_item.setText(0, menu.name)
                    size = self.getSizeUnit(menu.size)
                    menu_item.setText(1, size)
                    menu_item.setCheckState(0, QtCore.Qt.Checked)
                    for myfile in menu:
                        if type(myfile) == myfunc.FileList:
                            filelist_item = QtWidgets.QTreeWidgetItem(menu_item)
                            filelist_item.setFlags(filelist_item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                            filelist_item.setText(0, myfile.name)
                            size = self.getSizeUnit(myfile.size)
                            filelist_item.setText(1, size)
                            filelist_item.setCheckState(0, QtCore.Qt.Checked)
                            self.addFileListItem(filelist_item, myfile)
                            continue
                        file_item = QtWidgets.QTreeWidgetItem(menu_item)
                        file_item.setFlags(file_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                        file_item.setText(0, myfile.name)
                        size = self.getSizeUnit(myfile.size)
                        file_item.setText(1, size)
                        file_item.setCheckState(0, QtCore.Qt.Checked)

            else:
                l[0].setCheckState(0, QtCore.Qt.Checked)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            l = self.fileTree.findItems(item.text(0), QtCore.Qt.MatchExactly)
            if l != []:
                item.parent().removeChild(l[0])

    def addFileListItem(self, filelist_item, filelist):
        for myfile in filelist:
            if type(myfile) == myfunc.FileList:
                _filelist_item = QtWidgets.QTreeWidgetItem(filelist_item)
                _filelist_item.setFlags(_filelist_item.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
                _filelist_item.setText(0, myfile.name)
                size = self.getSizeUnit(myfile.size)
                _filelist_item.setText(1, size)
                _filelist_item.setCheckState(0, QtCore.Qt.Checked)
                self.addFileListItem(_filelist_item, myfile)
                continue
            file_item = QtWidgets.QTreeWidgetItem(filelist_item)
            file_item.setFlags(file_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            file_item.setText(0, myfile.name)
            size = self.getSizeUnit(myfile.size)
            file_item.setText(1, size)
            file_item.setCheckState(0, QtCore.Qt.Checked)

    def handleFileChange(self, item, column):
        item_name = item.text(0)
        if item.checkState(column) == QtCore.Qt.Checked:
            for course in self.account.course_list:
                if item_name == course.name:
                    return
                for menu in course:
                    if item_name == menu.name:
                        return
                    for myfile in menu:
                        if item_name == myfile.name and type(myfile) != myfunc.FileList:
                            self.download_list.append(myfile)
                            return
        else:
            for i in range(len(self.download_list)):
                if item_name == self.download_list[i]:
                    myfile.pop(i)
                    return

    def getSizeUnit(self, size):
        size = int(size)
        if size < 1073741824:
            size = size / 1048576
            size = round(size, 2)
            size = str(size) + ' MB'
        else:
            size = size / 1073741824
            size = round(size, 2)
            size = str(size) + ' GB'
        return size