import sys
import pymysql
import pandas
import random
from PyQt5.QtWidgets import *
from PyQt5 import uic

# Connection 연결
conn = pymysql.connect(host='', user='root', password='qwerty1', db='fs')
#conn = pymysql.connect(host='', user='root', password='yr10254528', db='fs')
# Cursor 생성
curs = conn.cursor()
# curs = conn.cursor(pymysql.cursors.DictCursor)

form_start_class = uic.loadUiType("fs_start.ui")[0]
form_search_class = uic.loadUiType("fs_search.ui")[0]
form_sresult_class = uic.loadUiType("fs_search_result.ui")[0]
form_grank_class = uic.loadUiType("goal_rank.ui")[0]
form_lrank_class = uic.loadUiType("league_rank.ui")[0]
form_mresult = uic.loadUiType("match_result.ui")[0]
form_mresult2 = uic.loadUiType("match_result2.ui")[0]
form_rank_class = uic.loadUiType('rank.ui')[0]


def match_sim(a, b):
    # 경기 돌리는 함수
    htid = a
    atid = b
    s_team = [[0] * 3 for i in range(3)]
    a_team = [[0] * 3 for i in range(3)]
    curs.execute(
        "SELECT p.pid, rating, h.position FROM player p, player_has_position h WHERE tid=(%s) AND p.pid=h.pid ORDER BY RAND() LIMIT 3;",
        (htid))
    # 팀에서 랜덤으로 3명의 pid와 능력치 뽑고 sql결과를 rows에 저장
    rows = curs.fetchall()
    select_team = pandas.DataFrame(rows)
    # 저장한 결과를 DF로

    for i in range(0, 3):
        for j in range(0, 3):
            s_team[i][j] = select_team[i][j]
    # DF를 다시 이차원 배열으로

    for i in range(0, 3):
        if 'GK' in s_team[2][i]:
            s_team[1][i] = 0
        elif 'D' in s_team[2][i]:
            s_team[1][i] = round((s_team[1][i] - 100) * 0.7)
        elif 'WB' in s_team[2][i]:
            s_team[1][i] = round((s_team[1][i] - 100) * 0.7)
        elif 'M' in s_team[2][i]:
            s_team[1][i] = round((s_team[1][i] - 100) * 0.9)
        elif 'ST' in s_team[2][i]:
            s_team[1][i] = round(s_team[1][i] - 90)
        elif 'F C' in s_team[2][i]:
            s_team[1][i] = round(s_team[1][i] - 90)
    # 뽑은 3명의 능력치를 포지션별로 확률 배당

    htgoal = 0
    for i in range(0, 3):
        if (random.randrange(1, 101) < s_team[1][i]):
            htgoal = htgoal + 1
            curs.execute("UPDATE player SET goal=goal+1 WHERE pid=(%s)",(int(s_team[0][i])))#선수 골 기록 추가
        else:
            break
    # 1~100중 랜덤으로 나온수가 계산한 확률보다 작으면 득점

    curs.execute(
        "SELECT p.pid, rating, h.position FROM player p, player_has_position h WHERE tid=(%s) AND p.pid=h.pid ORDER BY RAND() LIMIT 3",
        (atid))
    rows = curs.fetchall()
    against_team = pandas.DataFrame(rows)

    for i in range(0, 3):
        for j in range(0, 3):
            a_team[i][j] = against_team[i][j]

    for i in range(0, 3):
        if 'GK' in a_team[2][i]:
            a_team[1][i] = 0
        elif 'D' in a_team[2][i]:
            a_team[1][i] = round((a_team[1][i] - 100) * 0.7)
        elif 'WB' in a_team[2][i]:
            a_team[1][i] = round((a_team[1][i] - 100) * 0.7)
        elif 'M' in a_team[2][i]:
            a_team[1][i] = round((a_team[1][i] - 100) * 0.9)
        elif 'ST' in a_team[2][i]:
            a_team[1][i] = round(a_team[1][i] - 90)
        elif 'F C' in a_team[2][i]:
            a_team[1][i] = round(a_team[1][i] - 90)

    atgoal = 0
    for i in range(0, 3):
        if (random.randrange(1, 101) < a_team[1][i]):
            atgoal = atgoal + 1
            curs.execute("UPDATE player SET goal=goal+1 WHERE pid=(%s)",(int(a_team[0][i])))#선수 골 기록 추가
        else:
            break
    # 상대팀도 똑같이 진행

    curs.execute(
        "SELECT t1.tname, t2.tname FROM team t1, team t2 WHERE t1.tid=(%s) AND t2.tid=(%s)",
        (htid, atid))
    rows = curs.fetchall()

    curs.execute("INSERT INTO `match` (htid,atid,htgoal,atgoal) VALUES (%s,%s,%s,%s)",
    (htid,atid,htgoal,atgoal)) #경기 기록 업데이트
    if(htgoal>atgoal):
        curs.execute("UPDATE team SET point=point+3 WHERE tid=(%s)",(htid))
    elif(htgoal<atgoal):
        curs.execute("UPDATE team SET point=point+3 WHERE tid=(%s)",(atid))
    else:
        curs.execute("UPDATE team SET point=point+1 WHERE tid IN ((%s),(%s))",(htid,atid))
    conn.commit()


def goal_table():
    sql = "select p.pname, t.tname, p.goal from player p, team t where p.tid = t.tid order by p.goal desc limit 10;"
    curs.execute(sql)
    rows = curs.fetchall()
    goalRank = pandas.DataFrame(rows)
    global g_rank
    g_rank = [[0] * len(goalRank.index) for i in range(len(goalRank.columns))]

    for i in range(0, len(goalRank.columns)):
        for j in range(0, len(goalRank.index)):
            g_rank[i][j]=goalRank[i][j]


def league_table():
    sql = "SELECT tname, point FROM team order by point desc;"
    curs.execute(sql)
    rows = curs.fetchall()
    leagueRank = pandas.DataFrame(rows)
    global l_rank
    l_rank = [[0] * len(leagueRank.index) for i in range(len(leagueRank.columns))]
    for i in range(0, len(leagueRank.columns)):
        for j in range(0, len(leagueRank.index)):
            l_rank[i][j]=leagueRank[i][j]



for i in range (1,21):
        for j in range (1,21):
            if i==j:
                continue
            else:
                match_sim(i, j)
#반복문으로 리그 진행


def setCountry(uiCountry):
    global country
    country = uiCountry
    if (uiCountry == 'Any'):
        country = '%'
    else:
        country = uiCountry


def setPosition(uiPosition):
    global position
    position = uiPosition
    if (uiPosition == 'Any'):
        position = '%'
    else:
        position = uiPosition


def setTeam(uiTeam):
    global team
    if (uiTeam == 'Any'):
        team = '%'
    else:
        team = uiTeam


def setRating(uiRating_1):
    global rating1
    rating1 = uiRating_1


def setRating2(uiRating_2):
    global rating2
    rating2 = uiRating_2


def setName(uiName):
    global name1, name2
    name1 = uiName+'%'
    name2 = '%'+uiName
    if (uiName == 'Any'):
        name1 = '%'
        name2 = '%'
    else:
        name1 = uiName+'%'
        name2 = '%'+uiName


def searchResult():
    curs.execute("SELECT DISTINCT p.pname, t.tname, h.position, p.rating, n.nationality FROM player p, player_has_position h, team t, nationality n WHERE p.pid=h.pid AND  p.pid=n.pid AND p.tid=t.tid AND n.nationality LIKE (%s) AND h.position LIKE (%s) AND t.tname LIKE (%s) AND p.rating BETWEEN (%s) AND (%s) AND (p.pname LIKE (%s) OR p.pname LIKE (%s)) GROUP BY p.pname ORDER BY p.pname ASC",
                 (country,position,team,rating1,rating2,name1,name2))
    rows = curs.fetchall()
    sResultDF = pandas.DataFrame(rows)

    global sResultColumns
    sResultColumns = len(sResultDF.columns)
    global sResultIndex
    sResultIndex = len(sResultDF.index)

    global sResultArr
    sResultArr = [[0] * sResultIndex for n in range(sResultColumns)]
    for i in range(0, sResultColumns):  # 6
        for j in range(0, sResultIndex):  # 2
            sResultArr[i][j] = sResultDF[i][j]


def setsRowCount():
    return sResultIndex


def setmRowCount():
    return mResultIndex


def setTeamName(uiTname):
    global tname
    tname = uiTname


def goMatchResult():
    curs.execute("SELECT tid FROM team WHERE tname=(%s)",(tname))
    rows = curs.fetchall()
    tidDF = pandas.DataFrame(rows)
    tid=tidDF[0][0]
    curs.execute(
    "SELECT t1.tname, CONCAT(m1.htgoal,':',m1.atgoal) AS score, CASE WHEN (m1.htgoal-m1.atgoal)>0 THEN '승' WHEN (m1.htgoal-m1.atgoal)<0 THEN '패' ELSE '무' END result FROM team t1, `match` m1  WHERE m1.htid=(%s)  AND t1.tid=m1.atid  UNION ALL  SELECT t2.tname, CONCAT(m2.htgoal,':',m2.atgoal) AS score, CASE WHEN (m2.htgoal-m2.atgoal)>0 THEN '패' WHEN (m2.htgoal-m2.atgoal)<0 THEN '승' ELSE '무' END result FROM team t2, `match` m2  WHERE m2.atid=(%s)  AND t2.tid=m2.htid;",
    (int(tid),int(tid)))
    rows = curs.fetchall()
    mResultDF= pandas.DataFrame(rows)

    global mResultColumns
    mResultColumns = len(mResultDF.columns)
    global mResultIndex
    mResultIndex = len(mResultDF.index)

    global mResultArr
    mResultArr = [[0] * mResultIndex for n in range(mResultColumns)]
    for i in range(0, mResultColumns):  # 6
        for j in range(0, mResultIndex):  # 2
            mResultArr[i][j] = mResultDF[i][j]


curs.execute("DELETE FROM `match`;")
curs.execute("UPDATE player SET goal=0;")
curs.execute("UPDATE team SET point=0;")
conn.commit()
#기록 초기화

for i in range (1,21):
        for j in range (1,21):
            if i==j:
                continue
            else:
                match_sim(i, j)
#반복문으로 리그 진행


'''
############################     UI     #############################
'''

class StartWindow(QMainWindow, form_start_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.search)#1번째 버튼 클릭시 search 화면
        self.pushButton_2.clicked.connect(self.rank)#2번째 버튼 클릭시 rank화면
        self.pushButton_3.clicked.connect(self.match_result)#3번째 버튼 클릭시 match화면

    def search(self):
        searchWindow = SearchWindow(self)
        searchWindow.show()
        self.hide()

    def rank(self):
        rankWindow = RankWindow(self)
        rankWindow.show()
        self.hide()

    def match_result(self):
        mresult = MResultWindow(self)
        mresult.show()
        self.hide()


class SearchWindow(QMainWindow, form_search_class):
    def __init__(self, parent=None):
        super(SearchWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.search) #검색 버튼
        self.pushButton_2.clicked.connect(self.back) #뒤로 가기 버튼
        self.lineEdit.returnPressed.connect(self.setName)
        self.spinBox.valueChanged.connect(self.setRating)
        self.spinBox_2.valueChanged.connect(self.setRating2)

    def search(self):
        searchResult()
        sresultWindow = SresultWindow(self)
        sresultWindow.show()
        self.hide()

    def back(self): #뒤로가기
        startWindow.show()
        self.hide()

    def setCountry(self):
        uicountry=self.comboBox.currentText()
        setCountry(uicountry)

    def setPosition(self):
        uiposition = self.comboBox_2.currentText()
        setPosition(uiposition)

    def setTeam(self):
        uiteam=self.comboBox_3.currentText()
        setTeam(uiteam)

    def setRating(self):
        uirating=self.spinBox.value()
        setRating(uirating)

    def setRating2(self):
        uirating2=self.spinBox_2.value()
        setRating2(uirating2)

    def setName(self):
        uiname=self.lineEdit.text()
        setName(uiname)


class SresultWindow(QMainWindow, form_sresult_class):
    def __init__(self, parent=None):
        super(SresultWindow, self).__init__(parent)
        self.setupUi(self)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(sResultIndex)
        self.pushButton_2.clicked.connect(self.back)
        for i in range (0, 5):
            for j in range(0,setsRowCount()):
                self.tableWidget.setItem(j,i,QTableWidgetItem(str(sResultArr[i][j])))

    def back(self): #뒤로가기
        self.close()
        startWindow.show()


########################################################################
############################     RANK     #############################


class RankWindow(QMainWindow, form_rank_class):
    def __init__(self,parent=None):
        super(RankWindow,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.lrank) #리그 랭킹
        self.pushButton_2.clicked.connect(self.grank) #득점 랭킹
        self.pushButton_3.clicked.connect(self.back) #뒤로가기

    def lrank(self):
        league_table()
        lRankWindow = LRankWindow(self)
        lRankWindow.show()
        self.hide()

    def grank(self):
        goal_table()
        gRankWindow = GRankWindow(self)
        gRankWindow.show()
        self.hide()

    def back(self): #뒤로가기
        startWindow.show()
        self.hide()


class LRankWindow(QMainWindow, form_lrank_class):
    def __init__(self,parent=None):
        super(LRankWindow, self).__init__(parent)
        self.setupUi(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(20)
        self.pushButton_2.clicked.connect(self.back)
        for i in range(0, 2):
            for j in range(0, 20):
                self.tableWidget.setItem(j, i, QTableWidgetItem(str(l_rank[i][j])))

    def back(self):
        rankWindow = RankWindow(self)
        rankWindow.show()
        self.hide()

class GRankWindow(QMainWindow, form_grank_class):
    def __init__(self,parent=None):
        super(GRankWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.back)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(10)
        for i in range(0, 3):
            for j in range(0, 10):
                self.tableWidget.setItem(j, i, QTableWidgetItem(str(g_rank[i][j])))

    def back(self): #뒤로가기
        rankWindow = RankWindow(self)
        rankWindow.show()
        self.hide()

##########################################################################
#############################   RESULT   ###########################

class MResultWindow(QMainWindow, form_mresult):
    def __init__(self, parent=None):
        super(MResultWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.goMatchResult)
        self.pushButton_2.clicked.connect(self.back)
        self.comboBox.currentIndexChanged.connect(self.setTeamName)

    def goMatchResult(self):
        goMatchResult()
        mresult2Window = MResult2Window(self)
        mresult2Window.show()
        self.hide()

    def back(self): #뒤로가기
        startWindow.show()
        self.close()

    def setTeamName(self):
        tname=self.comboBox.currentText()
        setTeamName(tname)

class MResult2Window(QMainWindow, form_mresult2):
    def __init__(self, parent=None):
        super(MResult2Window, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.back)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(mResultIndex)
        for i in range (0, 3):
            for j in range(0,setmRowCount()):
                self.tableWidget.setItem(j,i,QTableWidgetItem(str(mResultArr[i][j])))

    def back(self): #뒤로가기
        mresultWindow = MResultWindow(self)
        mresultWindow.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    startWindow = StartWindow()
    startWindow.show()
    sys.exit(app.exec_())

# Connection 닫기
conn.close()