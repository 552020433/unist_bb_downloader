import re
import time
import os
from sys import exit
from base64 import b64encode as b64
from bs4 import BeautifulSoup
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

class LoginFail(Exception):
    pass

class Account():
    def __init__(self, student_id, pw):
        session = requests.Session()
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

        for i in soup.find_all("a", role="menuitem"):
            u = regex.findall(i['onclick'])
            u = u[0].strip("Course%26id%3D")
            course_list.append(Course(session, i.text,u))

        return course_list

class Course():
    def __init__(self, session, name, course_id):
        self.name = name
        self.id = course_id
        self.__menu_list = MenuList(session, self.id)
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

    def __init__(self, session, course_id):
        self.__menu_list = self.__getMenuList(session, course_id)
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

    def __getMenuList(self, session, course_id):
        course_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/courseMain?task=true&src="
        menu_list = []
        
        course_url = course_url + "&course_id=" + course_id
        html = getHTML(session, course_url)
        soup = BeautifulSoup(html, 'html.parser')
        for i in soup.select('.courseMenu .clearfix a'):
            if i.text in MenuList.not_accept_menu:
                continue
            menu_list.append(Menu(session, i.text, i['href']))
        return menu_list

class Menu():
    def __init__(self, session, name, url):
        self.name = name
        self.url = url
        self.__file_list = FileList(session, self.url, '')
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

class FileList():
    def __init__(self, session, menu_url, name):
        self.__file_list = self.__getFileList(session, menu_url)
        self.num = len(self.__file_list)
        self.name = name
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

    def __getFileList(self, session, menu_url):
        file_list = []
        if menu_url.find("http://") == -1:
            menu_url = "http://bb.unist.ac.kr" + menu_url
        html = getHTML(session, menu_url)

        soup = BeautifulSoup(html, 'html.parser')
        soup = soup.find("div", class_="contentBox")

        attached_s = soup.find_all("ul", class_="attachments clearfix")
        title_s = soup.select('.item a')
        if len(attached_s) == 0 and len(title_s) == 0:
            return []
        
        for i in attached_s:
            file_url = "http://bb.unist.ac.kr" + i.li.a["href"]
            file_url = self.__getFileLastUrl(session, file_url)
            file_name = i.li.a.text[1:]  # 맨 앞에 띄어쓰기 하나 있어서 지움
            file_list.append(File(session, file_name, file_url))
        
        for i in title_s:
            file_url = "http://bb.unist.ac.kr" + i["href"]
            file_name = i.text

            last_url = self.__getFileLastUrl(session, file_url)
            if last_url.find('webapps') != -1:
                file_list.append(FileList(session, last_url, file_name))
                continue

            regex = re.compile("\.[^\.]+[\?]")
            try:
                filetype = regex.findall(last_url)[0]
                if filetype[-1] == '?':
                    filetype = filetype[:-1]
            except:
                filetype = ""
            file_name += filetype

            file_list.append(File(session, file_name, last_url))

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
    def __init__(self, session, name, url):
        self.session = session
        self.name = name
        self.url = url
        self.size = self.__getFileSize(session, url)

    def __getFile(self):
        count = 0
        while True:
            try:
                p = self.session.post(self.url)
                my_file = p.content
            except:
                if count > 5:
                    errorExitMsg("파일 가져오기 실패", "파일을 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
                count += 1
                time.sleep(0.1)
                continue
            else:
                return my_file

    def saveFile(self, dir_path):
        file_path = os.path.join(dir_path, self.name)
        my_file = self.__getFile()
        with open(file_path, 'wb') as f:
            f.write(my_file)

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
            html = session.post(url, stream=True, data=data).text
        except:
            if count > 5:
                errorExitMsg("페이지 가져오기 실패", "HTML 페이지를 가져오는데 실패했습니다.\n\n인터넷 연결을 다시 확인해주세요..")
            count += 1
            time.sleep(0.1)
            continue
        else:
            return html

def getMenuContents(html, menu_name, dir_path):
    soup = BeautifulSoup(html, 'html.parser')
    s = soup.find("div", class_="contentBox")
    s = BeautifulSoup(s.prettify(), 'html.parser')
    try:
        for i in s.find_all("img"):
            i.decompose()
        s.find("div", class_="localViewToggle clearfix").decompose()
    except:
        pass

    if os.path.exists(os.path.join(dir_path, menu_name)):
        dir_path = os.path.join(dir_path, menu_name)

    file_name = menu_name+".html"
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", encoding="utf8") as f:
        f.write(str(s))

def downloadFiles(session, html, menu_name, dir_path):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find("div", class_="contentBox")

    attached_s = soup.find_all("ul", class_="attachments clearfix")
    title_s = soup.select('.item a')
    if len(attached_s) == 0 and len(title_s) == 0:
        return
    
    dir_path = os.path.join(dir_path, menu_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    for i in attached_s:
        file_url = "http://bb.unist.ac.kr" + i.li.a["href"]
        file_name = i.li.a.text[1:]  # 맨 앞에 띄어쓰기 하나 있어서 지움
        my_file = getFile(session, file_url)[0]
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(my_file)
    
    for i in title_s:
        file_url = "http://bb.unist.ac.kr" + i["href"]
        file_name = i.text

        my_file, last_url = getFile(session, file_url)
        regex = re.compile("\.[^\.]+\?")
        filetype = regex.findall(last_url)[0][:-1]
        file_name += filetype

        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(my_file)

def downloadMenu(session, menu_item, n, dir_path):
    menu_name = menu_item[n][0]
    if menu_item[n][1].find("http://") == -1:
        menu_url = "http://bb.unist.ac.kr" + menu_item[n][1]
    else:
        menu_url = menu_item[n][1]

    html = getHTML(session, menu_url)

    downloadFiles(session, html, menu_name, dir_path)
    getMenuContents(html, menu_name, dir_path)

