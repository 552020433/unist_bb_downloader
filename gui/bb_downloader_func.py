# bb_downloader_func.py

import re
import time
import os
import multiprocessing
from sys import exit
from base64 import b64encode as b64
from bs4 import BeautifulSoup
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

import os
import sys

## for pyinstaller
# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

class LoginFail(Exception):
    pass

class Account():
    def __init__(self, student_id, pw):
        session = requests.Session()
        session.trust_env = False
        self.session = self.__loginBB(session, student_id, pw)
        self.student_id = student_id

    def getCourseList(self):
        self.course_list = CourseList(self.session)

    def __loginBB(self, session, student_id, pw):
        login_url = "http://bb.unist.ac.kr"
        data = { 'user_id': student_id, 'password': '', 'encoded_pw': b64(pw.encode()) }
        html = getHTML(session, login_url, data=data)

        if html.find("Global Menu") == -1 and html.find("redirected to another page") == -1:
            raise LoginFail

        return session

class CourseList():
    def __init__(self, session):
        self.__course_list = self.__getCourseList(session)
        self.course_num = len(self.__course_list)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.course_num:
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.__course_list[index]

    def __getCourseList(self, session):
        course_list_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/globalCourseNavMenuSection?cmd=view&serviceLevel=blackboard.data.course.Course$ServiceLevel:FULL"
        html = getHTML(session, course_list_url)

        course_list = []
        soup = BeautifulSoup(html, 'html.parser')
        regex = re.compile("Course%26id%3D[0-9_]+")

        mp_list = []
        for i in soup.find_all("a", role="menuitem"):
            course_name = i.text
            course_id = regex.findall(i['onclick'])
            course_id = course_id[0].strip("Course%26id%3D")
            mp_list.append((session, course_name, course_id))

        with multiprocessing.Pool(4) as p:
            course_list = list(p.map(Course, mp_list))
        # for a, b, c in mp_list:
        #     course_list.append(Course((a, b, c)))
        return course_list

class Course():
    def __init__(self, args):
        session = args[0]
        name = args[1]
        course_id = args[2]

        self.name = name
        self.id = course_id

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        self.file_path = os.path.join(application_path, self.name)
        self.__menu_list = MenuList(session, self.id, self.file_path)
        self.menu_num = self.__menu_list.menu_num
        self.size = self.__getTotalSize()

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.menu_num:
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.__menu_list[index]

    def __getTotalSize(self):
        size = 0
        for menu in self:
            size += int(menu.size)
        return str(size)

class MenuList():
    not_accept_menu = ["WileyPLUS", "Discussion Board", "Messages", "Help", "Home"]

    def __init__(self, session, course_id, file_path):
        self.__menu_list = self.__getMenuList(session, course_id, file_path)
        self.menu_num = len(self.__menu_list)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.menu_num:
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.__menu_list[index]

    def __getMenuList(self, session, course_id, file_path):
        course_url = "http://bb.unist.ac.kr/webapps/Bb-mobile-bb_bb60/courseMap?"
        menu_list = []

        course_url = course_url + "course_id=" + course_id
        html = getHTML(session, course_url)
        soup = BeautifulSoup(html, 'html.parser')
        for i in soup.find('map').find_all('map-item', recursive=False):
            if i['name'] in MenuList.not_accept_menu:
                continue
            if i['linktype'] == "DIVIDER":  # 구분선 제외
                continue
            menu_list.append(Menu(session, i['name'], i, file_path))
        return menu_list

class Menu():
    def __init__(self, session, name, soup, file_path):
        self.name = name
        self.soup = soup
        self.url = soup['viewurl']
        if self.url.find("http://") == -1:
            self.url = "http://bb.unist.ac.kr" + self.url
        self.session = session
        self.file_path = os.path.join(file_path, self.name)
        self.__file_list = FileList(session, self.soup, '', self.file_path)
        self.file_num = self.__file_list.num
        self.size = self.__getTotalSize()

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.file_num:
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.__file_list[index]

    def __getTotalSize(self):
        size = 0
        for myfile in self:
            size += int(myfile.size)
        return str(size)

    def savePage(self):
        dir_path = os.path.dirname(self.file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        html = getHTML(self.session, self.url)
        soup = BeautifulSoup(html, 'html.parser')
        s = soup.find("div", class_="contentBox")
        s = BeautifulSoup(s.prettify(), 'html.parser')
        try:
            for i in s.find_all("img"):
                i.decompose()
            s.find("div", class_="localViewToggle clearfix").decompose()
        except:
            pass

        file_path = self.file_path + ".html"
        with open(file_path, "w", encoding="utf8") as f:
            f.write(str(s))

class FileList():
    def __init__(self, session, menu_soup, name, file_path):
        self.name = name
        if self.name == '':
            self.file_path = file_path
        else:
            self.file_path = os.path.join(file_path, self.name)

        self.__file_list = self.__getFileList(session, menu_soup, self.file_path)
        self.num = len(self.__file_list)
        self.size = self.__getTotalSize()

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.num:
            self.n += 1
            return self[self.n-1]
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.__file_list[index]

    def __getFileList(self, session, menu_soup, file_path):
        file_list = []
        file_soup = menu_soup.find('children')
        if file_soup == None:
            return []

        for i in file_soup.find_all('map-item', recursive=False):
            if i['isfolder'] == 'true':
                file_url = "http://bb.unist.ac.kr" + i['viewurl']
                file_name = i['name']
                _file_path = os.path.join(file_path, file_name)
                file_list.append(FileList(session, i, file_name, _file_path))
            else:
                file_soup = i.find('attachment')
                if file_soup == None:
                    continue
                file_url = "http://bb.unist.ac.kr" + file_soup['url']
                file_name = file_soup['name']
                # remove not allowed file character
                file_name = file_name.replace('/', '').replace('\\', '')
                _file_path = os.path.join(file_path, file_name)
                last_file_url = self.__getFileLastUrl(session, file_url)
                file_list.append(File(session, file_name, last_file_url, _file_path))

        return file_list

    def __getFileLastUrl(self, session, url, data=None):
        count = 0
        while True:
            try:
                p = session.post(url, stream=True, data=data)
                last_url = p.url
            except:
                if count > 5:
                    errorExitMsg("파일 url 가져오기 실패..", "파일 url을 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
                count += 1
                time.sleep(0.1)
                continue
            else:
                return last_url

    def __getTotalSize(self):
        size = 0
        for myfile in self:
            size += int(myfile.size)
        return str(size)

class File():
    def __init__(self, session, name, url, file_path):
        self.session = session
        self.name = name
        self.url = url
        self.file_path = file_path
        self.size = self.__getFileSize(session, url)

    def saveFile(self, downloadDialog, signal):
        dir_path = os.path.dirname(self.file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        count = 0
        while True:
            try:
                size = int(self.size)
                total_value = downloadDialog.TotalDownloadBar.value()
                signal.emit(size, 0, total_value)
                p = self.session.get(self.url, stream=True)

                file_data = b''
                for chunk in p.iter_content(chunk_size=1024*32):
                    file_data += chunk
                    signal.emit(size, len(file_data), total_value + len(file_data))
                    QtCore.QCoreApplication.processEvents()
            except:
                if count > 5:
                    errorExitMsg("파일 가져오기 실패", "파일을 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
                count += 1
                time.sleep(0.1)
                continue
            else:
                with open(self.file_path, 'wb') as f:
                    f.write(file_data)
                return

    def __getFileSize(self, session, url, data=None):
        count = 0
        while True:
            try:
                p = session.head(url, data=data)
            except:
                if count > 5:
                    errorExitMsg("파일 크기 가져오기 실패..", "header를 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
                count += 1
                time.sleep(0.1)
                continue
            try:
                file_size = p.headers['Content-Length']
            except:
                file_size = '0'

            return file_size


def errorExitMsg(msg_title, msg_body):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setWindowTitle(msg_title)
    msg.setText(msg_body)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    exit(msg.exec_())

def getHTML(session, url, data=None):
    count = 0
    while True:
        try:
            html = session.post(url, stream=False, data=data).text

        except:
            if count > 5:
                errorExitMsg("페이지 가져오기 실패", "HTML 페이지를 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
            count += 1
            time.sleep(0.1)
            continue
        else:
            return html
