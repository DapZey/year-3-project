//
// Created by benra on 8/24/2025.
//

#ifndef CLIENT_CONNECTWINDOW_H
#define CLIENT_CONNECTWINDOW_H
#include "raylib.h"
#include "string"
class ConnectWindow {
public:
    ConnectWindow(int width, int height);
    int screenwidth;
    int screenheight;
    int connectionStatus = 0;
    RaylibRectangle textareabounds;
    std::string text = "127.0.0.1";
    void draw();
    int getInput();
};


#endif //CLIENT_CONNECTWINDOW_H
