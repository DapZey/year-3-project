//
// Created by benra on 8/24/2025.
//

#include "ConnectWindow.h"
ConnectWindow::ConnectWindow(int width, int height) {
    this->screenheight = height;
    this->screenwidth = width;
    textareabounds = {float (screenwidth/4),
                      float (screenheight/3),
                      float (screenwidth/2),
                      float (screenheight/20)};
}
void ConnectWindow::draw() {
    BeginDrawing();
    ClearBackground(RAYWHITE);
    RaylibDrawText("Type gameserver IP and press enter to connect",
                   textareabounds.x, textareabounds.y -(screenwidth/60)-2,screenwidth/60,BLACK);
    DrawRectangleRec(textareabounds, GRAY);
    RaylibDrawText(text.c_str(),
                   textareabounds.x+3, textareabounds.y,
                   screenwidth/27,BLACK);
    DrawRectangleLinesEx(textareabounds, 2, BLACK);
    EndDrawing();
}
int ConnectWindow::getInput() {
    int key = GetKeyPressed();
    if (key >= KEY_ZERO && key <= KEY_NINE) {
        text += static_cast<char>('0' + (key - KEY_ZERO));
    }
    else if (key == KEY_PERIOD) {
        text += '.';
    }
    else if (key == KEY_BACKSPACE && !text.empty()) {
        text.pop_back();
    }
    if (text.length()>15){
        text.pop_back();
    }
    if (key == KEY_ENTER){
        return 1;
    }
    else {
        return 0;
    }
}