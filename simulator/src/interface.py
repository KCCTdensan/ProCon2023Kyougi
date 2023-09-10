import requests, json, datetime
import pandas as pd
from requests.exceptions import Timeout

class LogList:
    def __init__(self):
        self.time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        self.id = None
        while self.id is None:
            with open(r"..\interfaceLogs\nowId.txt", "r") as f:
                self.id = int(f.read())
        boolean = True
        while boolean:
            with open(r"..\interfaceLogs\nowId.txt", "w") as f:
                f.write(str(self.id+1))
                boolean = False
        self.data = pd.DataFrame(columns=["method", "url", "params", \
                                          "status", "reqTime", "resTime", \
                                          "data", "resData"])
        self.len = 0
    def add(self, method, url, **kwargs):
        newData = pd.DataFrame({"method": method, "url": url, \
                      "reqTime": datetime.datetime.now(), **kwargs}, \
                      index=[self.len])
        self.data = pd.concat([self.data, newData])
        self.len += 1
        return self.len-1
    def set(self, logId, status, data):
        self.data.at[logId, "resTime"] = datetime.datetime.now()
        self.data.at[logId, "status"] = status
        if data is not None: self.data.at[logId, "resData"] = data
    def __del__(self):
        if len(self.data) == 0:
            nowId = None
            while nowId is None:
                with open(r"..\interfaceLogs\nowId.txt", "r") as f:
                    nowId = int(f.read())
            if nowId != self.id+1: return
            boolean = True
            while boolean:
                with open(r"..\interfaceLogs\nowId.txt", "w") as f:
                    f.write(str(self.id))
                boolean = False
            return
        self.data.to_csv(f"..\\interfaceLogs\\log{self.id}({self.time}).csv")

d = datetime.timedelta(seconds=1)
class Field:
    def __init__(self, wall, territory, structure, mason):
        self.wall, self.territory, self.structure, self.mason = \
                   wall, territory, structure, mason
    def __str__(self):
        return ",".join(["  MyEn"[self.wall*2:][:2],
                         "  MyEnXX"[self.territory*2:][:2],
                         "    pondfort"[self.structure*4:][:4]],
                         f"{self.mason: >2}")
    def __repr__(self):
        return "".join(["Field({wall: ",
                        ["None", "MyWall", "EnemyWall"][self.wall],
                        ", territory: ",
                        ["None", "MyField", "EnemyField",
                         "BothField"][self.territory],
                        ", structure: ",
                        ["None", "Pond", "Castle"][self.structure],
                        ", mason: ",
                        str(self.mason),
                        "})"])

class Board:
    def __init__(self, board):
        self.walls = board["walls"]
        self.territories = board["territories"]
        self.width = board["width"]
        self.height = board["height"]
        self.mason = board["mason"]
        self.structures = board["structures"]
        self.masons = board["masons"]
        self.all = [[Field(*data) for data in zip(*datas)] for datas \
            in zip(self.walls, self.territories, self.structures, self.masons)]
        self.myMasons = [None]*self.mason
        self.opponentMasons = [None]*self.mason
        for x, row in enumerate(self.masons):
            for y, ans in enumerate(row):
                if ans > 0: self.myMasons[ans-1] = [x, y]
                if ans < 0: self.opponentMasons[-ans-1] = [x, y]
    def __str__(self):
        return "[{}]".format(",\n".join(str([*map(str, line)]) \
                                        for line in self.all))
    def __repr__(self):
        return "[{}]".format(",\n".join(map(repr, self.all)))

class MatchInfo:
    def __init__(self, info, match):
        self.id = info["id"]
        self.turn = info["turn"]
        self.board = Board(info["board"])
        self.logs = info["logs"]
        self.myTurn = info["id"]%2 == 1 ^ match["first"]
        self.myLogs = info["logs"][1-int(match["first"])::2]
        self.otherLogs = info["logs"][match["first"]::2]
    def __str__(self):
        return (f"id: {self.id}\n"
                f"turn: {self.turn}\n"
                 "board:\n"
                f"{self.board}\n"
                f"myTurn: {self.myTurn}\n"
                f"logs: {self.logs}\n"
                f"myLogs: {self.myLogs}\n"
                f"otherLogs: {self.otherLogs}")
    def __repr__(self):
        return "".join(["MatchInfo({id: ",
                        repr(self.id),
                        ", turn: ",
                        repr(self.turn),
                        ", myTurn: ",
                        repr(self.myTurn),
                        ",\nlogs: ",
                        repr(self.logs),
                        ",\nmyLogs: ",
                        repr(self.myLogs),
                        ",\notherLogs: ",
                        repr(self.otherLogs),
                        ",\nboard:\n",
                        repr(self.board)])

def matchInfo(info, match):
    if info is None: return None
    return MatchInfo(info, match)

class Interface:
    def __init__(self, token=None, *, baseUrl="http://localhost:", port=3000, \
                 check=True):
        self.log, self.token, self.id, self.turn, self.baseUrl = \
                  None, token, None, 0, "".join([baseUrl, str(port)])
        assert not check or self.getMatches(test=True) is not None, \
               f"token({token})が不正である可能性があります"
        self.checked = check
    def getMatches(self, *, test=False):
        if not test:
            assert self.checked, \
                   "正しいデータが挿入されていない可能性があります"
        res = self.get("/matches")
        if res is None: return None
        self.matches = res["matches"]
        return self.matches
    def setTo(self, matchId):
        assert self.checked, "正しいデータが挿入されていない可能性があります"
        for match in self.matches:
            if match["id"] == matchId: break
        else:
            raise IndexError(f"このid({matchId})の試合が見つかりませんでした\n"
                             "getMatches関数で確認してください")
        self.id, self.match = matchId, match
    def getMatchInfo(self):
        assert self.id is not None, \
               "試合Idを先に設定してください"
        res = matchInfo(self.get(f"/matches/{self.id}", \
                                 params={"id": self.id}), self.match)
        if res is None: return None
        self.turn = res.turn+1+int(res.turn%2 == 0 ^ self.match["first"])
        return res
    def setTurn(self, turn):
        self.turn = turn
    def postMovement(self, data):
        return self.post({"turn": self.turn, "actions": data})
        
    def get(self, url, **kwargs):
        url = "".join([self.baseUrl, url])
        params = {**kwargs.get("params", {}), "token": self.token}
        kwargs["params"] = params
        if self.log is None: self.log = LogList()
        for _ in range(3):
            logId = self.log.add("GET", url, **kwargs)
            try: res = requests.get(url, **kwargs, timeout=0.25)
            except Timeout:
                self.log.set(logId, 404, "")
                continue
            self.log.set(logId, res.status_code, res.text)
            if res.status_code == 200: break
        else:
            print("サーバとの通信に失敗しました。")
            return None
        data = json.loads(res.text)
        return data
    def post(self, **kwargs):
        url = "".join([self.baseUrl, f"/matches/{self.id}"])
        params = {**kwargs.get("params", {}), "token": self.token}
        kwargs["params"] = params
        if self.log is None: self.log = LogList()
        for _ in range(3):
            logId = self.log.add("POST", url, **kwargs)
            try: res = requests.post(url, **kwargs, timeout=0.25)
            except Timeout:
                self.log.set(logId, 404, "")
                continue
            self.log.set(logId, res.status_code, res.text)
            if res.status_code == 200: break
        else:
            print("サーバとの通信に失敗しました。")
            return False
        return True
    def release(self):
        self.log = None
