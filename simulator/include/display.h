#pragma once
#include <vector>

struct Color {
    float r;
    float g;
    float b;
};

int displayInit();
void drawDisplay(std::vector<std::vector<int>>& fieldData);
void displayOff();