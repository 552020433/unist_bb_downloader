import re
import time
from base64 import b64encode as b64
from getpass import getpass
import queue  # for pyinstaller
from bs4 import BeautifulSoup
import requests

def getHTML(session, url, data=None):
    while True:
        try:
            html = session.post(url, data=data).text
        except:
            print("페이지 연결 실패!")
            print("다시 연결을 시도합니다..\n")
            time.sleep(0.5)
            continue
        else:
            print("페이지 가져오기 성공!\n")
            return html

def loginBB(session, login_url):
    while True:
        student_id = input("학번을 입력하세요: ")
        pw = getpass("비밀번호를 입력하세요(보이지 않아도 입력되고 있는 중이에요!): ")

        data = { 'user_id': student_id, 'password': '', 'encoded_pw': b64(pw.encode()) }

        print("\n로그인 페이지를 가져오는 중입니다..")
        html = getHTML(session, login_url, data=data)

        if html.find("The username or password you entered is incorrect.") != -1:
            print("올바르지 못한 ID와 비밀번호 입니다 :(")
            print("다시 입력해주세요...\n")
            continue
        else:
            break
    return session

def parseCourseID(html):
    course_list = []
    soup = BeautifulSoup(html, 'html.parser')
    regex = re.compile("Course%26id%3D[0-9_]+")

    for i in soup.find_all("a", role="menuitem"):
        u = regex.findall(i['onclick'])
        u = u[0].strip("Course%26id%3D")
        course_list.append((i.text,u))

    return course_list

def parseMenu(html):
    menu_list = []
    soup = BeautifulSoup(html, 'html.parser')
    for i in soup.select('.courseMenu .clearfix a'):
        menu_list.append((i.text, i['href']))
    return menu_list

login_url = "http://bb.unist.ac.kr"
html_name = "test.html"

session = requests.Session()
session = loginBB(session, login_url)

course_list_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/globalCourseNavMenuSection?cmd=view&serviceLevel=blackboard.data.course.Course$ServiceLevel:FULL"
print("Course 리스트를 가져오는 중입니다..")
html = getHTML(session, course_list_url)
course_list = parseCourseID(html)

count = 1
print("---- 다운로드 가능한 과목 ----")
for i, j in course_list:
    print(str(count)+ ". " + i)
    count += 1
count -= 1

while True:
    try:
        n = int(input("무슨 과목을 다운로드할까요? (1-"+str(count-1)+"): "))
        if n < 1 or n > count:
            print("1부터 " + str(count) + "사이의 정수만 입력해 주세요!!")
            continue
    except ValueError:
        print("정수만 입력해주세요!")
        continue
    break

print("\n" + course_list[n-1][0] + " 페이지 가져오는 중..")
course_url = "http://bb.unist.ac.kr/webapps/blackboard/execute/courseMain?task=true&src="
course_url = course_url + "&course_id=" + course_list[n-1][1]
html = getHTML(session, course_url)
menu_list = parseMenu(html)