//
// Created by benra on 4/22/2025.
//

#include "Canvas.h"

Canvas::Canvas(int width, int height) {
   // std::cout<<width%3<<"\n";
    if (width%3 != 0 || width < minWidth){
        std::cerr<<"CANVAS WIDTH MUST BE DIVISIBLE BY THREE AND MUST MEET THE REQUIRED SIZE";
        exit(1);
    }
    if (height%3 != 0 || height < minHeight){
        std::cerr<<"CANVAS HEIGHT MUST BE DIVISIBLE BY THREE AND MUST MEET THE REQUIRED SIZE";
        exit(1);
    }
    canvasWidth = width;
    canvasHeight = height;
    canvasStartLeftX = (canvasWidth/3);
    std::cout<<canvasStartLeftX<<"\n";
    rendertexture2D = LoadRenderTexture(canvasStartLeftX*2,canvasHeight);
    BeginTextureMode(rendertexture2D);
    ClearBackground(RAYWHITE);
    EndTextureMode();
}
void Canvas::drawInfoBoard() {
    DrawRectangleRec({0,0,(float)canvasStartLeftX,(float)canvasHeight},drawBoardColor);
    RaylibDrawText("AI DRAW GAME",10,10,canvasStartLeftX/10,BLACK);
    RaylibDrawText("LEFT CLICK TO DRAW, BACKSPACE TO ERASE",10,100,canvasStartLeftX/30,BLACK);
    RaylibDrawText(TextFormat("CURRENT FPS: %i", GetFPS()), 10, 200, canvasStartLeftX/30, GREEN);
    if (erasor){
        RaylibDrawText("ERASOR ON",10,300,canvasStartLeftX/20,GREEN);
    }
    RaylibDrawText("CURRENT CATEGORY:",10,400,canvasStartLeftX/20,BLACK);
    RaylibDrawText(TextFormat("%s", category.c_str()),10,430,canvasStartLeftX/21,BLACK);

    RaylibDrawText(TextFormat("Categories left: %i", categoriesLeft),10,470,canvasStartLeftX/20,BLACK);
    RaylibDrawText(TextFormat("Opponent categories left: %i", categoriesLeftOpponent),10,500,canvasStartLeftX/20,BLACK);
}
void Canvas::drawCanvas() {
    if (IsKeyPressed(KEY_E)){
        erasor = !erasor;
    }
    if (!erasor){
        brushcolor = BLACK;
    }
    else {
        brushcolor = RAYWHITE;
    }
    if (IsKeyPressed(eraseKey)){
        BeginTextureMode(rendertexture2D);
        ClearBackground(RAYWHITE);
        EndTextureMode();
    }
    Vector2 mousePos = GetMousePosition();
    mousePos.x = mousePos.x-canvasStartLeftX;
    if (IsMouseButtonDown(drawbutton) && mousePos.x > 0){
//        std::cout<<mousePos.x<<"\n";
//        std::cout<<"drawing";
        BeginTextureMode(rendertexture2D);
        DrawCircle(mousePos.x,mousePos.y,drawCirleRadius,brushcolor);
        if (clickedPrev){
            if (mousePosPrev.x != mousePos.x || mousePosPrev.y != mousePos.y){
//                std::cout<<"drawing line\n";
                DrawLineEx({mousePosPrev.x, mousePosPrev.y}, {mousePos.x, mousePos.y},drawCirleRadius*2,brushcolor);
            }
        }
        EndTextureMode();
        clickedPrev = true;
    }
    else{
        clickedPrev = false;
    }

    BeginDrawing();
    ClearBackground(RAYWHITE);
    drawInfoBoard();
    DrawTexturePro(rendertexture2D.texture,{0,0,(float)rendertexture2D.texture.width,(float)-rendertexture2D.texture.height},{(float)canvasStartLeftX,0,(float)canvasStartLeftX*2,(float)canvasHeight},{0,0},0,WHITE);
    EndDrawing();
    mousePosPrev.y = mousePos.y;
    mousePosPrev.x = mousePos.x;
    if (IsMouseButtonReleased(drawbutton) || IsKeyReleased(eraseKey)){
        ReadyToSendImageInput = true;
        Image image = LoadImageFromTexture(rendertexture2D.texture);
        ImageFlipVertical(&image);
        ExportImage(image, "my_amazing_texture_painting.png");
        UnloadImage(image);
    }
}

Canvas::~Canvas() {
    UnloadRenderTexture(rendertexture2D);
}
