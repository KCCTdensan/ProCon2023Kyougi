#include "../include/display.h"
#include "../include/simulator.h"
#include <GL/gl.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>

// 画面サイズ
const int g_width = 1200;
const int g_height = 1200;

GLFWwindow* window;

// カラーコード
std::vector<Color> cl = {
    { 0xf0, 0xe6, 0x8c }, // 道
    { 0xff, 0x00, 0x00 }, // player1
    { 0x00, 0x00, 0xff }, // player2
    { 0x00, 0xC0, 0xC0 }, // 池
    { 0x69, 0x69, 0x69 }, // 城
};

// GUIを表示させる前に必ず実行すること
int displayInit()
{
    for (auto& x : cl) {
        x.r /= (float)0xff;
        x.g /= (float)0xff;
        x.b /= (float)0xff;
    }
    if (!glfwInit()) {
        return -1;
    }
    glfwSwapInterval(1);
    if (!glfwInit()) {
        return -1;
    }
    window = glfwCreateWindow(g_width, g_height, "sample", NULL, NULL);
    glfwMakeContextCurrent(window);
    return 0;
}

// 与えられたfieldDataを表示
void drawDisplay(std::vector<std::vector<int>>& fieldData)
{

    if (!window) {
        int displayCode = displayInit();
        if (displayCode == -1) {
            std::cout << "glfwInitが実行できませんでした。display.cpp:12" << std::endl;
            glfwTerminate();
            return;
        }
        if (!window) {
            std::cout << "windowを生成できませんでした。display.cpp:19" << std::endl;
            glfwTerminate();
            return;
        }
    }

    // イベントの処理
    glfwPollEvents();

    // 描画処理
    glClear(GL_COLOR_BUFFER_BIT); // カラーバッファをクリア

    glLoadIdentity();
    glTranslatef(0.0f, 0.0f, -1.0f); // 平行移動

    for (int r = 1; r <= height; r++) {
        for (int c = 1; c <= width; c++) {
            // 正方形の描画
            float y1 = 1.0f - (2.0f / (height + 2)) * r, x1 = -1.0f + (2.0f / (width + 2)) * c, y2 = 1.0f - (2.0f / (height + 2)) * (r + 1), x2 = -1.0f + (2.0f / (width + 2)) * (c + 1);
            glBegin(GL_QUADS);
            auto t = personFind(Pos(r, c)).first;
            if (t != -1) {
                glColor3f(cl[t].r, cl[t].g, cl[t].b);
            } else {
                glColor3f(cl[fieldData[r - 1][c - 1]].r, cl[fieldData[r - 1][c - 1]].g, cl[fieldData[r - 1][c - 1]].b); // 色の設定
            }
            glVertex2f(x1, y2); // 左下
            glVertex2f(x2, y2); // 右下
            glVertex2f(x2, y1); // 右上
            glVertex2f(x1, y1); // 左上
            glEnd();
        }
    }
    glfwSwapBuffers(window);
}

// displayを消す(最後には必ず実行すること)
void displayOff()
{
    glfwTerminate();
}