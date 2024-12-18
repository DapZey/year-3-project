#include "raylib.h"
#include "vector"
#include <cstdlib>
#include <cmath>
#include "deque"
#include "boost/asio.hpp"
#include "iostream"
#include "thread"
#include "atomic"
#include <fstream>
#include <queue>

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
struct ThreadInfo {
    std::unique_ptr<std::thread> thread;
    std::atomic<bool> should_join{false};
};
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
ThreadInfo thread_info;
void sendImage(boost::asio::io_context& io_context,
               boost::asio::ip::tcp::socket& socket,
               Image tosend) {
    const char* START_DELIMITER = "<IMAGE_START>";
    const char* END_DELIMITER = "<IMAGE_END>";

    ImageFlipVertical(&tosend);
    ExportImage(tosend, "output.png");
    try {
        // Send start delimiter
        boost::asio::write(socket, boost::asio::buffer(START_DELIMITER, strlen(START_DELIMITER)));

        std::ifstream file("output.png", std::ios::binary);
        if (!file) {
            std::cerr << "Failed to open output.png" << std::endl;
            return;
        }

        const size_t buffer_size = 1024;
        char buffer[buffer_size];
        while (file.read(buffer, buffer_size) || file.gcount() > 0) {
            boost::asio::write(socket, boost::asio::buffer(buffer, file.gcount()));
        }

        // Send end delimiter
        boost::asio::write(socket, boost::asio::buffer(END_DELIMITER, strlen(END_DELIMITER)));
        std::cout << "Image sent successfully." << std::endl;
    } catch (const boost::system::system_error& e) {
        std::cerr << "Error sending image: " << e.what() << std::endl;
    }

    SetWindowIcon(tosend);
    UnloadImage(tosend);
    thread_info.should_join = true;
}

std::atomic<bool> stop_recv{false};
std::queue<std::string> data_queue;   // Shared queue
std::mutex queue_mutex;               // Mutex to protect access to the queue

void receiver(boost::asio::ip::tcp::socket& socket) {
    char buffer[1024];
    while (!stop_recv) {
        try {
            // Non-blocking receive attempt (may need a timeout or non-blocking socket)
            size_t len = socket.receive(boost::asio::buffer(buffer));
            if (len > 0) {
                std::string data(buffer, len);
                {
                    std::lock_guard<std::mutex> lock(queue_mutex);
                    data_queue.push(data);
                }
            }
        } catch (const boost::system::system_error& e) {
            std::cerr << "Error in receive: " << e.what() << std::endl;
            if (e.code() == boost::asio::error::operation_aborted) {
                break;
            }
        }
    }
}

int main() {
    InitWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "Drawing Game");
//    SetTargetFPS(TARGET_FPS);
    RenderTexture2D drawingCanvas = LoadRenderTexture(2 * (WINDOW_WIDTH/3), WINDOW_HEIGHT);
    BeginTextureMode(drawingCanvas);
    ClearBackground(BLANK);
    EndTextureMode();
    RaylibRectangle source = {0, 0, static_cast<float>(drawingCanvas.texture.width), static_cast<float>(-drawingCanvas.texture.height)};
    RaylibRectangle sourceYFlipped = {0, 0, static_cast<float>(drawingCanvas.texture.width), static_cast<float>(drawingCanvas.texture.height)};
    RaylibRectangle dest = {WINDOW_WIDTH / 3, 0, 2 * (WINDOW_WIDTH / 3), WINDOW_HEIGHT};

    float Player1Score = 0;
    float Player2score = 0;
    int brushSize = 3;
    RaylibRectangle imageDrawingBounds = {WINDOW_WIDTH / 3, 0, 2 * (WINDOW_WIDTH / 3), WINDOW_HEIGHT};
    Color TEXT_COLOR = (Color){ 76, 82, 112, 255 };
    Color BG_COLOR = (Color){ 188, 236, 224, 255 };
    Color ALT_COLOR_STRONG = (Color){ 246, 82, 160, 255 };
    Color ALT_COLOR_WEAK = (Color){ 54, 238, 224, 255 };
    std::vector<int> rgbSelectorValues = {255, 0, 0};

    Vector2 lastMousePos = {0, 0};
    bool wasMouseDown = false;
    std::deque<RenderTexture2D> savedCanvasVersions;
    int canvasIndex = 0;
    using boost::asio::ip::tcp;
    boost::asio::io_context io_context;

    // we need a socket and a resolver
    tcp::socket socket(io_context);
    tcp::resolver resolver(io_context);
    // now we can use connect(..)
    try {
        boost::asio::connect(socket, resolver.resolve("127.0.0.1", "8000"));
    } catch (const boost::system::system_error& ex){
        std::cerr<< "\nFailed to connect to server\nTerminating...";
        exit(-2);
    }
    std::thread receive_thread([&socket]() { receiver(socket); });
    while (!WindowShouldClose()) {
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            while (!data_queue.empty()) {
                std::string data = data_queue.front();
                data_queue.pop();
                std::cout << "Processing data: " << data << std::endl;
                // Do something with the data (e.g., rendering, game logic)
            }
        }
        if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT)){
            canvasIndex = (int)savedCanvasVersions.size()-1;
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
            ClearBackground(WHITE);
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
            canvasIndex--;
            if (canvasIndex <0){
                canvasIndex = (int)savedCanvasVersions.size()-1;
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
        RaylibDrawText(TextFormat("Your Drawing Score: %f", Player1Score), 20, 20, 25, TEXT_COLOR);
        RaylibDrawText(TextFormat("Opponent Drawing Score: %f", Player1Score), 20, 50, 25, TEXT_COLOR);
        RaylibDrawText(TextFormat("Time Left: %f", Player1Score), 20, 100, 30, TEXT_COLOR);
        RaylibDrawText("press the letters R,G,B to change rgb\n R,G,B + CNTRL to change by 10 \n R,G,B + SPACE to change by 100", 20, 250, 30, TEXT_COLOR);
        RaylibDrawText(TextFormat("R: %d G: %d B: %d", rgbSelectorValues[0], rgbSelectorValues[1], rgbSelectorValues[2]), 20, 400, 30, TEXT_COLOR);
        RaylibDrawText("COLOR: \n(ENTER_KEY to change brush size)", 20, 450, 30, TEXT_COLOR);
        RaylibDrawText("Image To Draw: ", 20, 680, 30, TEXT_COLOR);
        DrawCircle(150, 460, brushSize * 5,
                   (Color){ static_cast<unsigned char>(rgbSelectorValues[0]),
                            static_cast<unsigned char>(rgbSelectorValues[1]),
                            static_cast<unsigned char>(rgbSelectorValues[2]),
                            255});
        DrawTexturePro(drawingCanvas.texture, source, dest, (Vector2){0, 0}, 0.0f, WHITE);
        RaylibDrawText(TextFormat("CURRENT FPS: %i",GetFPS()), 0, 600, 20, GREEN);
        EndDrawing();
        if (IsKeyPressed(KEY_LEFT_SHIFT) && !thread_info.thread) {
            Image im = LoadImageFromTexture(drawingCanvas.texture);
            thread_info.should_join = false; // Reset join flag
            thread_info.thread = std::make_unique<std::thread>(
                    [&]() { sendImage(io_context, socket, im); });
        }

        if (thread_info.thread && thread_info.should_join) {
            if (thread_info.thread->joinable()) {
                thread_info.thread->join();
                thread_info.thread.reset();
                std::cerr<<"joining thread\n";
            }
        }
    }
    stop_recv = true;
    socket.shutdown(boost::asio::ip::tcp::socket::shutdown_both);
    socket.close();
    receive_thread.join();
    UnloadRenderTexture(drawingCanvas);
    for (RenderTexture2D texture : savedCanvasVersions){
        UnloadRenderTexture(texture);
    }
    if (thread_info.thread) {
        thread_info.thread->join();
    }
    RaylibCloseWindow();
    return 0;
}
