import requests, json
import pandas as pd
import datetime
baseUrl = "http://localhost:3000"

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
def matchInfo(info, match):
    info["myTurn"] = info["id"]%2 == 1 ^ match["first"]
    info["myLogs"] = info["logs"][1-int(match["first"])::2]
    info["otherLogs"] = info["logs"][match["first"]::2]
    return info

class Interface:
    def __init__(self, token):
        self.log, self.token, self.id, self.turn = LogList(), token, None, 0
        assert self.getMatches() is not None, \
               f"token({token})が不正である可能性があります"
    def getMatches(self):
        res = self.get("/matches")
        if res is None: return None
        self.matches = res["matches"]
        return self.matches
    def setTo(self, matchId):
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
        self.turn = res["turn"]+1+int(res["turn"]%2 == 0 ^ self.match["first"])
        return res
    def setTurn(self, turn):
        self.turn = turn
    def postMovement(self, data):
        self.post({"turn": self.turn, "actions": data})
        
    def get(self, url, **kwargs):
        url = "".join([baseUrl, url])
        params = {**kwargs.get("params", {}), "token": self.token}
        kwargs["params"] = params
        for _ in range(3):
            logId = self.log.add("GET", url, **kwargs)
            res = requests.get(url, **kwargs, timeout=1)
            self.log.set(logId, res.status_code, res.text)
            if res.status_code == 200: break
        else:
            print("サーバとの通信に失敗しました。")
            return None
        data = json.loads(res.text)
        return data
    def post(self, **kwargs):
        url = "".join([baseUrl, f"/matches/{self.id}"])
        params = {**kwargs.get("params", {}), "token": self.token}
        kwargs["params"] = params
        for _ in range(3):
            logId = self.log.add("POST", url, **kwargs)
            res = requests.post(url, **kwargs, timeout=1)
            self.log.set(logId, res.status_code, res.text)
            if res.status_code == 200: break
        else:
            print("サーバとの通信に失敗しました。")
            return False
        return True
    def release(self):
        self.log = LogList()
