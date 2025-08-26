//
// Created by benra on 8/24/2025.
//

#ifndef CLIENT_WAITINGWINDOW_H
#define CLIENT_WAITINGWINDOW_H

#include "raylib.h"
#include "string"
#include "vector"
class waitingWindow {
public:
    std::vector<std::string> texts = {"waiting for players...", "YOU WON!", "YOU LOST"};
    waitingWindow(int width, int height);
    int screenwidth;
    int screenheight;
    std::string messageText;
    void draw();
};


#endif //CLIENT_WAITINGWINDOW_H
