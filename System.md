# システム説明書
競技を行うシステムは以下の要素で構成されている。
・src/control.py：競技を行う際はここからシステムを開始する。また複数のアルゴリズムを管理でき、試合を管理するクラスも存在する。
・src/interface.py：競技APIとの通信を簡単に行うためのクラスが実装されている。また、ログファイルの出力もここから行う。
・src/simulator.py：競技に関する様々なクラス、関数が実装されている。試合情報を管理するクラス、コーディング上で頻繁に使用する関数などが存在する。
・src/view.py：GUIでの表示を行うためのモジュール。
・src/solveList.py：複数のアルゴリズムを全て読み込むためのモジュール。
・src/logClear.py：ログファイルを消去するためのファイル。
また、これ以外のpythonファイルは基本的に行動を決定するアルゴリズムが実装されている。

・src/result/solverList.txt：現在利用可能なアルゴリズムのデータ。
・src/result/disabledList.txt：現在利用不能なアルゴリズムのデータ。
また、src/result内部に存在するcsvファイルは練習段階での試合結果を保存した物である。

・interfaceLogs.nowId.txt：現在のログ番号のデータ。
interfaceLogsフォルダには通信のログが保存される。

また、fieldDatasフォルダには全てのフィールドに対して複数のターン数、ターン時間のデータが存在する。

以下にクラス及び関数の説明を示す。なお、便宜上職人の行動を決定するアルゴリズムのことをsolver関数と呼ぶ。

・control.mode
このファイルには複数のモードが実装されており、ここから動作させるモードを変更させることが出来る。

・class control.Result(solver, *, update=False)
練習段階において試合結果を保持するクラス。引数のsolverにはsolver関数を表す拡張子付きの文字列を渡す必要がある。新規に作成されたsolver関数の場合updateをTrueにすることで新たなデータが作成される。
Result.result：辞書の中にpandas.DataFrameによる試合結果を格納する。DataFrameのindexは全てのsolver関数の先手、後手に対応する文字列、columnsは全てのフィールドに対応する文字列となる。
Result.all()：ターン数、1ターンの時間を全通り含めたジェネレータ関数。
Result.match(other, field)：指定のフィールドにおいて、指定のsolver関数との試合結果を返す。先手、後手の順の配列が返される。otherには拡張子付きのsolver関数を、fieldにはフィールドの文字列、ターン数、ターン時間を含む配列を渡す(例：["A11", 30, 3])。
Result.set(other, field, point1, point2, result, *, first=True)：試合結果を保存する関数。
  other：拡張子付きのsolver関数
  field：試合情報を表す配列
  point1：自身の総得点
  point2：相手の総得点
  result：勝敗を表すbool
  first：先手、後手を表すbool
Result.release()：試合結果をクラス内からファイルへ出力する。

・class control.Solver(solver)
solver関数を保持、実行するクラス。引数のsolverには拡張子付きのsolver関数を渡す。
Solver.threading(func, *args, **kwargs)：並列処理を行う関数。
Solver.solve(func, *args, **kwargs)：solver関数を実行する関数。
Solver.start(interface)：interfaceをsolver関数に渡し、実行する。interfaceは後述するinterface.Interfaceクラスである。
Solver.targetAs(target)：solver関数がフィールドに対応しているかどうか判定する。targetにはフィールドの文字列を渡す。
Solver.isAlive()：Solver関数が実行されているかどうかを返す。
Solver.release()：Solver関数を停止させる。

・class control.Match()
試合を管理するクラス。
Match.interfaceStart(interface, matchId, token, **kwargs)：interfaceの設定を行う。interfaceはinterface.Interfaceクラスであり、matchId、token、**kwargsはサーバーに通信するための情報を表す。
Match.threading(func, *args, **kwargs)：並列処理を行う関数。
Match.keep(func, *args, **kwargs)：渡された関数を実行し、結果をMatch.returnedとして記録する。threadingによる並列化で返り値が必要なときに使う。
Match.show()：GUI表示を行う。内部で後述するview.show関数を呼び出している。

・class control.Real(solver, matchId)
試合を管理するクラス。外部のサーバーと通信する、本番用のものである。
solverには拡張子付きのsolver関数を、matchIdには試合のIdを渡す。
Real.isAlive()：試合が続行されているかどうかを返す。

・class control.Practice(solver1, solver2, field, port)
試合を管理するクラス。内部でサーバーを立ち上げてsolver関数を2つ起動する、練習用のものである。
solver1には先手、solver2には後手の拡張子付きのsolver関数を、fieldには試合情報を表す配列を、portにはサーバーを立ち上げるポート番号を渡す。
Practice.isAlive()：試合が続行されているかどうかを返す。
Practice.release(*, safety=False)：試合を終了し、interfaceに対してリリース作業を行う。safetyにFalseを渡すことでログを残さずに終了する。safetyは高速にプログラムを終了させたい時に必要となる。

・control.pattern(solver1, solver2)
練習時、solver1とsolver2に対しての全ての試合パターンを返すジェネレータ関数。"all"から全てのsolver関数への変換もここで行う。

・control.practiceStart(target, po)
練習時、試合を非同期で立ち上げる関数。

・interface.dataBool
ログを残すかどうかを決定する変数。

・interface.recordBool
完全なログを残すかどうかを決定する変数。

・class interface.LogFileId()
ログ番号を管理するクラス。
LogFileId.get()：ログ番号をインクリメントし、現在のログ番号を返す。
LogFileId.now()：現在のログ番号を返す。
LogFileId.set()：ログ番号を設定する。
LogFileId.release()：ログ番号をファイルに保存する。

・interface.logFileId
LogFileIdクラスのインスタンス。このインスタンスがログ番号を管理する。

・interface.release()
interface.logFileId.release()を呼び出す。

・class interface.LogList()
通信ログを保存するクラス。
LogList.add(method, url, **kwargs)：ログを追記する。また、通信終了時にログ番号を返す。基本的にリクエスト送信時に実行される。
LogList.set(logId, status, data)：指定されたログ番号に対するログに情報を追加する。基本的にリクエストに対する応答の受信時に実行される。

・interface.matchInfo(info, match)
infoがNoneであればNoneを、でなければ後述のsimulator.MatchInfoクラスを返す。

・class interface.Interface(token=None, *, baseUrl="http://loclahost:", port=3000, check=True)
サーバーと通信するためのクラス。token,baseUrl,portにはサーバーと通信するために必要な情報を渡す。check=Falseとすることでインスタンス化のみを先に行うことが出来る。
Interface.getMatches(*, test=False)：試合情報の一覧を取得する。/matchesに対してGETリクエストを送信し、そのレスポンスをpythonオブジェクトに変換して返す。test=Trueの場合初期化が完了していないインスタンスで実行することが出来る。これは初期化が正常に行われたか確認するためのものである。
Interface.setTo(matchId)：インスタンスに試合Idを指定する。これによって指定されたIdの試合に対する通信を行うようになる。
Interface.getMatchInfo()：試合情報を取得する。/matches/{self.id}に対してGETリクエストを送信する。そのレスポンスをpythonオブジェクトに変換してからinterface.matchInfoに渡し、simulator.MatchInfoクラスとして返す。
Interface.setTurn(turn)：次に職人の行動を送信する際のターン数を指定する。
Interface.postMovement(data)：職人の行動を送信する。dataにはいくつかの形式が対応している(README.md参照)。/matches/{self.id}に対してPOSTリクエストを送信し、成功したかどうかをboolで返す。
Interface.get(url)：サーバーにGETリクエストを送信し、その結果をpythonオブジェクトに変換して返す。この関数の内部でログを記録する。
Interface.get(url)：サーバーにPOSTリクエストを送信する。この関数の内部でログを記録する。
Interface.relase(safety=True)：インスタンスを無効化し、LogListクラスを消去することでログのリセット及び記録を行う。safetyをFalseとするとログのリセットは行わない。

・class simulator.Field(wall, territory, structure, mason)
フィールド上の1マス部分を表すクラス。
Field.wall, Field.territory, Field.structure, field.masonがそれぞれ初期化の際の引数に対応する。

・class simulator.Board(board)
フィールドの状況を表すクラス。内部に行動決定のためのアルゴリズムを実装したメソッドも存在する。
boardには/matches/{id}に対するGETリクエストのレスポンスの"board"部分をpythonオブジェクトに変換したものを渡す。
Board.height：board["height"]の情報。
Board.width：board["width"]の情報。
Board.mason：board["mason"]の情報。
Board.walls：board["walls"]の情報。
Board.territories：board["territories"]の情報。
Board.structures：board["structures"]の情報。
Board.masons：board["masons"]の情報。
Board.all：Fieldクラスの2次元配列。これによって一括でwalls,territories,structures,masonsの情報を取得することができる。
Board.myMasons：自チームの職人の位置を表すlistの配列。
Board.otherMasons：他チームの職人の位置を表すlistの配列。
Board.castles：城の位置を表すlistの配列。
Board.inField(x, y=None)：与えられた座標がフィールドの中に存在するか否かboolで返す。y=Noneの場合、xが座標の配列になっているものとして処理する。以下、デフォルト値にNoneが指定されている場合は同様の処理。
Board.allDirection(x, y, directions=None)：x, yに対してdirectionsの内容を順に加算し、新たな座標を返すジェネレータ関数。
Board.distance(x, y=None)：与えられた座標からの距離を幅探索し、2次元配列で返す。到達できない箇所は-1が返される。存在しない座標が与えられるとNoneを返す。
Board.nearest(pos, targets)：targetsのうちposから最も近いものを返す。存在しない座標が与えられるとNoneを返す。
Board.outline(targets, directions)：与えられたtargetsの輪郭を返す。
Board.around(targets, directions)：与えられたtargetsに対してdirectionsだけ座標をずらしたときの全ての位置を返す。
Board.calcPoint()：現在の自チームの点数、相手チームの点数を返す。

・class simulator.MatchInfo(info, match)
試合の現在の状況を表すクラス。
MatchInfo.turn：現在のターン数
MatchInfo.turns：この試合の総ターン数
MatchInfo.myTurn：次のターンが自分のターンか否か (先手チームならturn = [0, 2, 4, 6...]の時にTrue)
MatchInfo.first：この試合において自分が先手か否か
MatchInfo.board：現在のフィールドの情報をBoardクラスで表したもの
MatchInfo.logs：過去の職人の行動
MatchInfo.myLogs：MatchInfo.logsから自チームのターンのみ取り出したもの
MatchInfo.otherLogs：MatchInfo.logsから相手チームのターンのみ取り出したもの

・view.drawField(canvas, field, x, y, x0, length)
canvasに対してフィールドの1マスを描写する。canvasにはtkinter.Canvasクラスを、fieldにはsimulator.Fieldクラスを、x, yにはマスの座標を、x0にはx方向の初期値を、lengthには1マスの大きさを渡す。
・view.main()
GUI表示を行う。
・view.start()
view.main()の並列処理を開始する。
・view.show()
GUIに新たなデータを渡す。
・view.release()
GUI表示を停止する。


競技時の主な流れを以下に示す。

control.pyのmodeを0に指定して実行する(ファイル内の値を変えることでmodeを指定する)。
Realクラスに指定されたSolverクラスが渡され、Interfaceクラスがサーバーと通信を行う。
Interfaceクラスの確認が終わるとsolver関数が実行され、Interfaceクラスを介して試合を行う。GUIを有効化している場合はGUI表示も行う。