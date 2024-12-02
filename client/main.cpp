#include "raylib.h"
#include "vector"
#include <stdlib.h>
#include <math.h>
#include "deque"
#include "iostream"

#define WINDOW_WIDTH 1920
#define WINDOW_HEIGHT 1080
#define TARGET_FPS 1000

// Lerp function for Vector2
Vector2 Vector2Lerp(Vector2 start, Vector2 end, float t) {
    return (Vector2){
            start.x + (end.x - start.x) * t,
            start.y + (end.y - start.y) * t
    };
}

void changeRGB(std::vector<int>& rgbSelectorValues, int index) {
    if (IsKeyDown(KEY_SPACE)) {
        rgbSelectorValues[index] += 100;
    }
    else if (IsKeyDown(KEY_LEFT_CONTROL)) {
        rgbSelectorValues[index] += 10;
    }
    else {
        rgbSelectorValues[index] += 1;
    }
    if (rgbSelectorValues[index] > 255) {
        rgbSelectorValues[index] -= 255;
    }
}

int main() {
    InitWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "Drawing Game");
    SetTargetFPS(TARGET_FPS);

    RenderTexture2D drawingCanvas = LoadRenderTexture(2 * (WINDOW_WIDTH/3), WINDOW_HEIGHT);
    BeginTextureMode(drawingCanvas);
    ClearBackground(BLANK);
    EndTextureMode();
    Rectangle source = {0, 0, static_cast<float>(drawingCanvas.texture.width), static_cast<float>(-drawingCanvas.texture.height)};
    Rectangle sourceYFlipped = {0, 0, static_cast<float>(drawingCanvas.texture.width), static_cast<float>(drawingCanvas.texture.height)};
    Rectangle dest = {WINDOW_WIDTH/3, 0, 2*(WINDOW_WIDTH/3), WINDOW_HEIGHT};

    float Player1Score = 0;
    float Player2score = 0;
    int brushSize = 3;
    Rectangle imageDrawingBounds = {WINDOW_WIDTH/3, 0, 2*(WINDOW_WIDTH/3), WINDOW_HEIGHT};
    Color TEXT_COLOR = (Color){ 76, 82, 112, 255 };
    Color BG_COLOR = (Color){ 188, 236, 224, 255 };
    Color ALT_COLOR_STRONG = (Color){ 246, 82, 160, 255 };
    Color ALT_COLOR_WEAK = (Color){ 54, 238, 224, 255 };
    std::vector<int> rgbSelectorValues = {255, 0, 0};

    Vector2 lastMousePos = {0, 0};
    bool wasMouseDown = false;
    std::deque<RenderTexture2D> savedCanvasVersions;
    int canvasIndex = 0;
    while (!WindowShouldClose()) {
        if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT)){
            RenderTexture2D currentCanvas = LoadRenderTexture(2 * (WINDOW_WIDTH/3), WINDOW_HEIGHT);
            BeginTextureMode(currentCanvas);
            DrawTextureV(drawingCanvas.texture,{0,0}, WHITE);
            EndTextureMode();
            savedCanvasVersions.push_back(currentCanvas);
            if (savedCanvasVersions.size() >5){
                UnloadRenderTexture(savedCanvasVersions[0]);
                savedCanvasVersions.pop_front();
            }
        }
        if (IsMouseButtonDown(MOUSE_BUTTON_LEFT)) {
            if (CheckCollisionPointRec(GetMousePosition(), imageDrawingBounds)) {
                Vector2 currentMousePos = {
                        GetMousePosition().x - WINDOW_WIDTH/3,
                        GetMousePosition().y
                };

                BeginTextureMode(drawingCanvas);
                if (!wasMouseDown) {
                    DrawCircle(currentMousePos.x, currentMousePos.y, brushSize*5,
                               (Color){ static_cast<unsigned char>(rgbSelectorValues[0]),
                                        static_cast<unsigned char>(rgbSelectorValues[1]),
                                        static_cast<unsigned char>(rgbSelectorValues[2]),
                                        255});
                } else {
                    float distance = sqrtf(powf(currentMousePos.x - lastMousePos.x, 2) +
                                           powf(currentMousePos.y - lastMousePos.y, 2));
                    int numPoints = (int)(distance / (brushSize * 2)) + 1;
                    for (int i = 0; i <= numPoints; i++) {
                        float t = (float)i / numPoints;
                        Vector2 pos = Vector2Lerp(lastMousePos, currentMousePos, t);
                        DrawCircle(pos.x, pos.y, brushSize*5,
                                   (Color){ static_cast<unsigned char>(rgbSelectorValues[0]),
                                            static_cast<unsigned char>(rgbSelectorValues[1]),
                                            static_cast<unsigned char>(rgbSelectorValues[2]),
                                            255});
                    }
                }
                EndTextureMode();
                lastMousePos = currentMousePos;
                wasMouseDown = true;
            }
        } else {
            wasMouseDown = false;
        }
        if (IsKeyPressed(KEY_BACKSPACE)){
            BeginTextureMode(drawingCanvas);
            ClearBackground(BLANK);
            EndTextureMode();
        }
        if (IsKeyPressed(KEY_R)) {
            changeRGB(rgbSelectorValues, 0);
        }
        if (IsKeyPressed(KEY_G)) {
            changeRGB(rgbSelectorValues, 1);
        }
        if (IsKeyPressed(KEY_B)) {
            changeRGB(rgbSelectorValues, 2);
        }
        if (IsKeyPressed(KEY_ENTER)) {
            brushSize++;
            if (brushSize > 5) {
                brushSize = 1;
            }
        }
        if (IsKeyPressed(KEY_RIGHT)){
            canvasIndex++;
            if (canvasIndex > 4){
                canvasIndex = 0;
            }
            BeginTextureMode(drawingCanvas);
            ClearBackground(WHITE);
            DrawTextureV(savedCanvasVersions[canvasIndex].texture,{0,0}, WHITE);
            EndTextureMode();
        }
        BeginDrawing();
        ClearBackground(RAYWHITE);

        // Draw the UI elements
        DrawRectangle(0, 0, WINDOW_WIDTH/3, WINDOW_HEIGHT, BG_COLOR);
        DrawRectangle(0, 720, WINDOW_WIDTH/3, WINDOW_HEIGHT/3, ALT_COLOR_STRONG);
        DrawText(TextFormat("Your Drawing Score: %f", Player1Score), 20, 20, 25, TEXT_COLOR);
        DrawText(TextFormat("Opponent Drawing Score: %f", Player1Score), 20, 50, 25, TEXT_COLOR);
        DrawText(TextFormat("Time Left: %f", Player1Score), 20, 100, 30, TEXT_COLOR);
        DrawText("press the letters R,G,B to change rgb\n R,G,B + CNTRL to change by 10 \n R,G,B + SPACE to change by 100", 20, 250, 30, TEXT_COLOR);
        DrawText(TextFormat("R: %d G: %d B: %d", rgbSelectorValues[0], rgbSelectorValues[1], rgbSelectorValues[2]), 20, 400, 30, TEXT_COLOR);
        DrawText("COLOR: \n(ENTER_KEY to change brush size)", 20, 450, 30, TEXT_COLOR);
        DrawText("Image To Draw: ", 20, 680, 30, TEXT_COLOR);
        DrawCircle(150, 460, brushSize * 5,
                   (Color){ static_cast<unsigned char>(rgbSelectorValues[0]),
                            static_cast<unsigned char>(rgbSelectorValues[1]),
                            static_cast<unsigned char>(rgbSelectorValues[2]),
                            255});
            DrawTexturePro(drawingCanvas.texture, source, dest, (Vector2){0, 0}, 0.0f, WHITE);
        DrawText(TextFormat("CURRENT FPS: %i",GetFPS()), 0, 600, 20, GREEN);
        EndDrawing();
    }
    UnloadRenderTexture(drawingCanvas);
    for (RenderTexture2D texture : savedCanvasVersions){
        UnloadRenderTexture(texture);
    }
    savedCanvasVersions.clear();
    CloseWindow();
    return 0;
}
