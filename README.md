# ProCon2023Kyougi

## ファイルのビルド方法

### 1. meson と ninja のインストール

`pip3 install meson`

`pip3 install ninja`

### 2. ファイルのビルド

```bash
pwd
/ProCon2023Kyougi/simulator
```

このディレクトリにいる状態で以下のコマンドを実行

```bash
meson setup ./build --reconfigure
ninja -C ./build
```

これで`simulator`という実行ファイルが`/ProCon2023Kyougi/simulator/build`内にできるので、あとはこれを実行すればプログラムを実行できます。

## ビルドするファイルの増やし方

`meson.build`の中の`src`に追加すればおｋ

## このプロジェクトをビルドするのに必要な外部ライブラリ

- OpenGL
- GLFW

これらを導入できない場合は`meson.build`の中の`display.cpp`を消し、`simulator.cpp`の`#define GL`をコメントアウトすればビルドできるようになるはずです(多分)
