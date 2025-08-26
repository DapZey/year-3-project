//
// Created by benra on 8/24/2025.
//

#include "waitingWindow.h"
waitingWindow::waitingWindow(int width, int height) {
    this->screenwidth = width;
    this->screenheight = height;
    messageText =  texts[0];
}
void waitingWindow::draw() {
    BeginDrawing();
    ClearBackground(RAYWHITE);
    RaylibDrawText(messageText.c_str(),float (screenwidth/4),
                   float (screenwidth/3),screenwidth/60,BLACK);
    EndDrawing();
}