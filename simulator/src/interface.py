import httpx, json, datetime, platform
import pandas as pd
from requests.exceptions import Timeout, ConnectionError
from simulator import MatchInfo

if platform.system() == "Windows":
    logFile = "..\\interfaceLogs\\"
else:
    logFile = "../interfaceLogs/"

class LogList:
    def __init__(self):
        self.time = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
        self.id = None
        while self.id is None:
            with open(f"{logFile}nowId.txt", "r") as f:
                if (txt := f.read()) != "": self.id = int(txt)
        boolean = True
        while boolean:
            with open(f"{logFile}nowId.txt", "w") as f:
                f.write(str(self.id+1))
                boolean = False
        self.data = pd.DataFrame(columns=["method", "url", "headers", \
                                          "params", "status", "reqTime", \
                                          "resTime", "data", "resData"])
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
                with open(f"{logFile}nowId.txt", "r") as f:
                    nowId = int(f.read())
            if nowId != self.id+1: return
            boolean = True
            while boolean:
                with open(f"{logFile}nowId.txt", "w") as f:
                    f.write(str(self.id))
                boolean = False
            return
        self.data.to_csv(f"{logFile}log{self.id}({self.time}).csv")

def matchInfo(info, match):
    if info is None: return None
    return MatchInfo(info, match)

class Interface:
    def __init__(self, token=None, *, baseUrl="http://localhost:", port=3000, \
                 check=True):
        self.log, self.token, self.id, self.turn, self.baseUrl = \
                  None, token, None, 0, f"{baseUrl}{port}"
        self.headers = {"procon-token": token}
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
        res = matchInfo(self.get(f"/matches/{self.id}"), self.match)
        if res is None: return None
        self.turn = res.turn+1+int(res.turn%2 == 0 ^ self.match["first"])
        return res
    def setTurn(self, turn):
        self.turn = turn
    def postMovement(self, data):
        if type(data) is not list: pass
        elif type(data[0]) is list:
            old, data = data, {"turn": self.turn}
            data["actions"] = []
            for d in old:
                data["actions"].append({"type": d[0], "dir": d[1]})
        elif type(data[0]) is dict:
            data = {"turn": self.turn, "actions": data}
        return self.post(f"/matches/{self.id}", data=data)
        
    def get(self, url):
        url = "".join([self.baseUrl, url])
        if self.log is None: self.log = LogList()
        logId = self.log.add("GET", url, headers=self.headers)
        try:
            with httpx.Client(timeout=httpx.Timeout(0.5)) as client:
                res = client.get(url, headers=self.headers)
            if res.status_code == httpx.codes.OK:
                if self.log is None: return None
                self.log.set(logId, res.status_code, res.json())
                return res.json()
            code = res.status_code
        except (httpx.TimeoutException, httpx.NetworkError): code = 404
        if self.log is not None: self.log.set(logId, code, "")
        print(f"サーバとの通信に失敗しました。({logId}: {code})")
        return None
    def post(self, url, data):
        url = "".join([self.baseUrl, url])
        if self.log is None: self.log = LogList()
        logId = self.log.add("POST", url, data=str(data), headers=self.headers)
        try:
            with httpx.Client(timeout=httpx.Timeout(0.5)) as client:
                res = client.post(url, json=data, headers=self.headers)
            if res.status_code == httpx.codes.OK:
                if self.log is None: return None
                self.log.set(logId, res.status_code, res.json())
                return True
            code = res.status_code
        except (httpx.TimeoutException, httpx.NetworkError): code = 404
        if self.log is not None: self.log.set(logId, code, "")
        print(f"サーバとの通信に失敗しました。({logId}: {code})")
        return False
    def release(self):
        self.log = None
