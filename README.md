# ProCon2023Kyougi

## ファイルのビルド方法

### 1. meson と ninja のインストール

`pip3 install meson`

windows で ninja-build をインストールする方法はまた今度調べます... <- pipでいけました

### 2. ファイルのビルド

```bash
pwd
/ProCon2023Kyougi/simulator
```

このディレクトリにいる状態で以下のコマンドを実行

```bash
meson setup ./build
ninja -C ./build
```

これで`simulator`という実行ファイルが`/ProCon2023Kyougi/simulator/build`内にできるので、あとはこれを実行すればプログラムを実行できます。
