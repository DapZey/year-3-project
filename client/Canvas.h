//
// Created by benra on 4/22/2025.
//

#ifndef CLIENT_CANVAS_H
#define CLIENT_CANVAS_H

#include "raylib.h"
#include "iostream"
#include "Network.h"
class Canvas {
public:
    std::string category = "-";
    int categoriesLeft = 10;
    int categoriesLeftOpponent = 10;
    std::string aiPredictedText = "-";
    int minWidth = 800;
    int minHeight = 600;
    Canvas(int width, int height);
    int canvasWidth;
    int canvasHeight;
    int canvasStartLeftX;

    bool erasor = false;

    ~Canvas();

    MouseButton drawbutton = MOUSE_BUTTON_LEFT;
    KeyboardKey eraseKey = KEY_BACKSPACE;
    int drawCirleRadius = 7;
    void drawCanvas();
    Vector2 mousePosPrev = {};
    bool clickedPrev = false;
    Color brushcolor = BLACK;

    RenderTexture2D rendertexture2D;

    void drawInfoBoard();
    Color drawBoardColor = RED;

    bool ReadyToSendImageInput = false;

    void ResetCanvas();

    void ClearCanvas();
};


#endif //CLIENT_CANVAS_H
