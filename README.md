# ProCon2023Kyougi

## 必要なライブラリ

httpx, pandas

`pip install httpx pandas`

`pip3 install httpx pandas`

## solverの追加方法(python)

### 1. srcにファイルを用意する

solverファイルは必ずsimulatorをインポートすること(行頭に`import simulator`)

ファイルの終端に`simulator.set("solver_name", solverFunc)`が必要

### 2. solveList.pyに追記する

solveList.pyの終端に`import solverFileName`を付け加える

### 3. control.pyで追加処理を行う

削除・変更したい場合は追加する際と同様にすると元に戻せる

## solver関数の作成方法について

solver関数はシミュレート時呼び出され、試合の情報を取得したり職人の行動を決定することが出来ます 必ず引数は以下の形式に従ってください

`def solverFunc(interface, solver)`

自作クラスについて以下に示します

### Interfaceクラス

solver関数の第1引数のinterfaceにはInterfaceクラスが渡されます 内容は以下の通りです

```
Interface.getMatchInfo(): MatchInfoクラス
  試合の情報がMatchInfoクラスで返される(後述) 通信に失敗した場合はNoneが返り値

Interface.postMovement(data): bool
  職人の行動を決定する(サーバーにPOSTする) 通信に失敗した場合はFalseが返り値
  dataの形式は2通り利用できる
    [[0, 0], [1, 8], [2, 8]]
    [{"type": 0, "dir": 0}, {"type": 1, "dir": 8}, {"type": 2, "dir": 8}]
  基本的に次の自分のターンに対しての行動を決定する

Interface.setTurn(turn): None
  Interface.postMovementの直前に使用することで次のターン以外にも行動を設定することが出来る
  他チームの行動は多分無理
```

MatchInfoクラス、及び内部に生成されるBoardクラスの内容は以下の通りです

### MatchInfoクラス
```
MatchInfo.turn: int
  現在のターン数
MatchInfo.myTurn: bool
  次のターンが自分のターンか否か (先手チームならturn = [0, 2, 4, 6...]の時にTrue)
MatchInfo.first: bool
  この試合において自分が先手か否か
MatchInfo.board: Boardクラス
  現在のフィールドの情報をBoardクラスで表したもの
MatchInfo.logs: list
  過去の職人の行動 詳しくは公式の試合状態取得API Responsesのlogsへ
    例
    {
      "turn": 1,
      "actions": [
        {
          "succeeded": true,
          "type": 0,
          "dir": 0
        }
      ]
    }
MatchInfo.myLogs: list
  MatchInfo.logsから自チームのターンのみ取り出したもの
MatchInfo.otherLogs: list
  MatchInfo.logsから相手チームのターンのみ取り出したもの
```

### Boardクラス
```
Board.height, Board.width: int
  フィールドの大きさ フィールドを2次元配列で表す際は長さheightの配列の中に長さwidthの配列が入る形になる
Board.mason: int
  職人の人数 自他共に同じ人数の職人がいる
Board.walls: list<list<int>>
  城壁の存在を表す2次元配列 {0: なし, 1: 自チームの城壁, 2: 他チームの城壁}
Board.territories: list<list<int>>
  陣地の情報を表す2次元配列 {0: なし, 1: 自チーム, 2: 他チーム, 3: 両チーム}
Board.structures: list<list<int>>
  構造物の情報を表す2次元配列 {0: 平地, 1: 池, 2: 城}
Board.masons: list<list<int>>
  職人の存在を表す2次元配列
  自然数は自チームの職人、負の数は他チームの職人 絶対値が職人のidを表す 0の時不在
Board.all: list<list<Fieldクラス>>
  2次元配列で表される情報をまとめたもの Fieldクラスは以下の通り
    Field.wall: int    Field.territory: int    Field.structure: int    Field.mason: int
    いずれも2次元配列から取り出す場合の値と同じ
Board.myMasons: list
  自チームの職人の位置を返す idが1始まりなのに対しインデックスは0始まりなので注意
    例: Board.myMasons[0] が [3, 6] のとき Board.masons[3][6] は 1
Board.otherMasons: list
  他チームの職人の位置を返す
Board.castles: list
  フィールド上の城の位置を返す
```

### Solverクラス

solver関数の第2引数のsolverにはSolverクラスが渡されます solver関数内で利用するのは次のメソッドのみです

```
solver.isAlive(): bool
  試合が続行可能かどうかを返す
```

Falseが返された場合即座にsolver関数を終了してください(終了処理を円滑に進めるため)

### simulatorモジュール

solverファイルに必ずインポートする必要があるsimulatorモジュールには便利な変数及び関数を用意しておきました 以下に示します

```
simulator.set(name, solver): None
  solverをsolver関数として登録する
  control.pyではnameを用いて管理するため注意すること 拡張子は不要 ファイル名に指定できない文字は指定不可

simulator.directionList: ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))
simulator.directionSet: ((1, -1, -1), (2, 0, -1), (3, 1, -1), (4, 1, 0), (5, 1, 1), (6, 0, 1), (7, -1, 1), (8, -1, 0))
simulator.fourDirectionList: ((0, -1), (1, 0), (0, 1), (-1, 0))
simulator.fourDirectionSet: ((2, 0, -1), (4, 1, 0), (6, 0, 1), (8, -1, 0))
  全方位にアクセスする際のインデックスの差分及びそのidをタプルにしたもの

simulator.inField(board, x, y): bool
  与えられた座標がBoardクラスの中に存在するか否かを返す
  次のように使ってください
    for dir, dx, dy: simulator.directionSet:
      newX, newY = x+dx, y+dy
      if not simulator.inField(board, newX, newY)

  引数を2つにして座標の配列で渡すこともできます
  simulator.inField(board, [500000, -123]) -> False

simulator.distance(board, x, y): list<list<int>>
  与えられた座標からの距離を幅探索し、2次元配列で返します 到達できない箇所は-1が返されます

simulator.calcPoint(board): list<list<int>>
  与えられたBoardクラスでの現在の自チームの点数、相手チームの点数を返します
  [
    [自チームの合計点数, 自チームの城のみの点数, 自チームの陣地のみの点数],
    [相手チームの合計点数, 相手チームの城のみの点数, 相手チームの陣地のみの点数]
  ]
```

## 試合結果について

試合結果はcontrol.pyで確認できますがresultフォルダからも確認できます

solver関数が異常終了した場合は点数を-1として記録します

なお、試合中が正常終了しなかった場合(Ctrl-Cで中断された場合等)は記録されません
