import re
import time
import os
from base64 import b64encode as b64
from getpass import getpass
import queue  # for pyinstaller
from bs4 import BeautifulSoup
import requests

def getHTML(session, url, data=None):
    count = 0
    while True:
        try:
            html = session.post(url, data=data).text
        except:
            if count > 5:
                print("인터넷 연결을 확인하신 후 다시 실행시켜주세요...")
                os.system("PAUSE")
                exit(-1)
            count += 1
            print("페이지 연결 실패!")
            print("다시 연결을 시도합니다..\n")
            time.sleep(1)
            continue
        else:
            print("페이지 가져오기 성공!\n")
            return html

def getFile(session, url, data=None):
    count = 0
    while True:
        try:
            my_file = session.post(url, data=data).content
        except:
            if count > 5:
                print("인터넷 연결을 확인하신 후 다시 실행시켜주세요...")
                os.system("PAUSE")
                exit(-1)
            count += 1
            print("파일 다운로드 실패!")
            print("다시 연결을 시도합니다..\n")
            time.sleep(1)
            continue
        else:
            print("파일 다운도르 성공!\n")
            return my_file

def loginBB(session):
    login_url = "http://bb.unist.ac.kr"
    while True:
        student_id = input("학번을 입력하세요: ")
        pw = getpass("비밀번호를 입력하세요(보이지 않아도 입력되고 있는 중이에요!): ")

        data = { 'user_id': student_id, 'password': '', 'encoded_pw': b64(pw.encode()) }

        print("\n로그인 페이지를 가져오는 중입니다..")
        html = getHTML(session, login_url, data=data)

        if html.find("Global Menu") == -1 and html.find("redirected to another page") == -1:
            print("올바르지 못한 ID와 비밀번호 입니다 :(")
            print("다시 입력해주세요...\n")
            continue
        else:
            break
    return session

def getCourseList(session):
    course_list_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/globalCourseNavMenuSection?cmd=view&serviceLevel=blackboard.data.course.Course$ServiceLevel:FULL"
    print("Course 리스트를 가져오는 중입니다..")
    html = getHTML(session, course_list_url)
    course_list = parseCourseID(html)
    
    return course_list

def parseCourseID(html):
    course_list = []
    soup = BeautifulSoup(html, 'html.parser')
    regex = re.compile("Course%26id%3D[0-9_]+")

    for i in soup.find_all("a", role="menuitem"):
        u = regex.findall(i['onclick'])
        u = u[0].strip("Course%26id%3D")
        course_list.append((i.text,u))

    return course_list

def printCourse(course_list):
    course_count = 1
    print("---- 다운로드 가능한 과목 ----")
    for i, j in course_list:
        print(str(course_count)+ ". " + i)
        course_count += 1

def getCourseInput(course_num):
    while True:
        try:
            n = int(input("무슨 과목을 다운로드할까요? (1-"+str(course_num)+"): "))
            if n < 1 or n > course_num:
                print("1부터 " + str(course_num) + "까지의 정수만 입력해 주세요!!")
                continue
        except ValueError:
            print("정수만 입력해주세요!")
            continue
        break
    return n

def getMenuList(session, course_list, n):
    print("\n" + course_list[n-1][0] + " 페이지 가져오는 중..")
    course_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/courseMain?task=true&src="
    course_url = course_url + "&course_id=" + course_list[n-1][1]

    html = getHTML(session, course_url)
    menu_list = parseMenu(html)

    return menu_list

def parseMenu(html):
    menu_list = []
    soup = BeautifulSoup(html, 'html.parser')
    for i in soup.select('.courseMenu .clearfix a'):
        if i.text == "Home" or i.text == "Messages" or i.text == "Help" or i.text == "Discussion Board":
            continue
        menu_list.append((i.text, i['href']))
    return menu_list

def printMenu(menu_list):
    print("---- 다운로드 가능한 항목 ----")
    menu_count = 1
    for i, j in menu_list:
        print(str(menu_count) + ". " + i)
        menu_count += 1

def getMenuInput(menu_num):
    while True:
        s = input("다운로드할 항목을 모두 선택해주세요(ex. 2 3): ")
        l = s.split()
        try:
            l = [int(x) for x in l]
        except ValueError:
            print("정수만 입력해주세요!\n")
            continue
        if l == []:
            continue
        if min(l) < 1 or max(l) > menu_num:
            print("1-" + str(menu_num) + " 사이 값만 넣어주세요!\n")
            continue
        break
    l = list(set(l))
    l.sort()
    return l

def getMenuContents(html, menu_name, dir_path):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        for i in soup.find_all("img"):
            i.decompose()
        soup.find("div", class_="localViewToggle clearfix").decompose()
    except:
        pass

    s = soup.find("div", class_="contentBox")
    if os.path.exists(os.path.join(dir_path, menu_name)):
        dir_path = os.path.join(dir_path, menu_name)

    file_name = menu_name+".html"
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, "w", encoding="utf8") as f:
        f.write(str(s))

    print(file_path, "저장 완료!")

def downloadFiles(session, html, menu_name, dir_path):
    soup = BeautifulSoup(html, 'html.parser')
    s = soup.find_all("ul", class_="attachments clearfix")
    if len(s) == 0:
        return
    
    dir_path = os.path.join(dir_path, menu_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    for i in s:
        file_url = "http://bb.unist.ac.kr" + i.li.a["href"]
        file_name = i.li.a.text[1:]  # 맨 앞에 띄어쓰기 하나 있어서 지움
        print(file_name, "를 다운로드하는 중입니다...")
        my_file = getFile(session, file_url)
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb') as f:
            f.write(my_file)

def downloadMenu(session, menu_list, n, dir_path):
    menu_name = menu_list[n][0]
    if menu_list[n][1].find("http://") == -1:
        menu_url = "http://bb.unist.ac.kr" + menu_list[n][1]
    else:
        menu_url = menu_list[n][1]

    print('\n' + menu_name, "페이지를 가져오는 중입니다...")
    html = getHTML(session, menu_url)

    downloadFiles(session, html, menu_name, dir_path)
    getMenuContents(html, menu_name, dir_path)

if __name__ == '__main__':
    while True:
        print("\n\n---- BB Downloader v0.1 ----")
        session = requests.Session()
        session = loginBB(session)

        course_list = getCourseList(session)

        printCourse(course_list)
        course_num = len(course_list)
        
        n = getCourseInput(course_num)
        course_name = course_list[n-1][0]

        menu_list = getMenuList(session, course_list, n)
        menu_num = len(menu_list)
        printMenu(menu_list)

        dir_path = os.path.join(os.path.dirname(__file__), course_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        menu_selected = getMenuInput(menu_num)
        for i in menu_selected:
            downloadMenu(session, menu_list, i-1, dir_path)