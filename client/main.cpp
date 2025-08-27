#include <iostream>
#include "raylib.h"
#include "Network.h"
#include "Canvas.h"
#include "algorithm"
#include "ConnectWindow.h"
#include "waitingWindow.h"
#include <vector>
#include <string>

enum Gamestate{
    connectwindowstate,
    waitingstate,
    playingstate,
};

// Global buffer to accumulate received data
std::string messageBuffer = "";

// Function to parse messages from buffer
std::vector<std::string> parseMessages(const std::string& data) {
    std::vector<std::string> messages;
    messageBuffer += data;

    size_t start = 0;
    size_t end = 0;
    while ((start = messageBuffer.find('|', end)) != std::string::npos) {
        end = messageBuffer.find('|', start + 1);
        if (end != std::string::npos) {
            std::string message = messageBuffer.substr(start + 1, end - start - 1);
            messages.push_back(message);
            end++;
        } else {
            break;
        }
    }
    if (end != std::string::npos && end > 0) {
        messageBuffer = messageBuffer.substr(end);
    }

    return messages;
}

int main() {
    const int screenWidth = 1290;
    const int screenHeight = 860;
    std::string password;
    InitWindow(screenWidth, screenHeight, "AIV2");
    SetTargetFPS(500);
    Network network;
    network.startup();
    Gamestate gamestate = connectwindowstate;
    Canvas canvas(screenWidth,screenHeight);
    ConnectWindow connectWindow(screenWidth, screenHeight);
    waitingWindow waitingWindow(screenWidth,screenHeight);

    bool connected = false;

    while (!WindowShouldClose())
    {
        if (gamestate == playingstate){
            canvas.drawCanvas();
        }
        if (gamestate == waitingstate){
            waitingWindow.draw();
        }
        if (gamestate == connectwindowstate){
            connectWindow.draw();
            if (connectWindow.getInput() == 1 && !connected){
                std::cout << "Attempting connection...\n";
                int connectionTry = 1;
                connectionTry = network.init(connectWindow.text, 1);
                if (connectionTry == 0){
                    std::cout << "Network init successful\n";
                    connectionTry = network.createSocket();
                    if (connectionTry == 0) {
                        std::cout << "Socket creation successful\n";
                        connectionTry = network.connectToServer();
                        if (connectionTry == 0) {
                            std::cout << "Connection to server successful\n";
                            connected = network.sendData("req");
                            if (connected) {
                                std::cout << "Request sent successfully\n";
                            } else {
                                std::cout << "Failed to send request\n";
                            }
                        } else {
                            std::cout << "Failed to connect to server\n";
                        }
                    } else {
                        std::cout << "Failed to create socket\n";
                    }
                } else {
                    std::cout << "Failed to initialize network\n";
                }
            }
        }
        if (canvas.ReadyToSendImageInput && network.imagereceived){
            canvas.ReadyToSendImageInput = false;
            network.imagereceived = false;
            network.sendLocalImageData("my_amazing_texture_painting.png", password);
        }
        if (IsKeyDown(KEY_ENTER) && gamestate == waitingstate && waitingWindow.messageText != waitingWindow.texts[0]){
            waitingWindow.messageText = waitingWindow.texts[0];
            gamestate = connectwindowstate;
            canvas.ResetCanvas();
            connected = false;
        }

        // Receive data and parse messages
        std::string rawData = network.receiveData();
        if (!rawData.empty()) {
            std::vector<std::string> messages = parseMessages(rawData);

            // Process each complete message
            for (const std::string& x : messages) {
                std::cout << "Received message: " << x << "\n";

                if (x[0] == 'w' && x[1] == ':'){
                    gamestate = waitingstate;
                }
                if (x[0] == 's' && x[1] == ':'){
                    gamestate = playingstate;
                    network.imagereceived = true;
                }
                if (x[0] == 'e' && x[1] == 'r'){
                }
                if (x[0] == 'c' && x[1] == ':'){
                    std::string category = x.substr(2);
                    canvas.category = category;
                }
                if (x[0] == 't' && x[1] == ':'){
                    std::string count = x.substr(2);
                    canvas.categoriesLeft = std::stoi(count) + 1;
                    canvas.ClearCanvas();
                }
                if (x[0] == 'o' && x[1] == ':'){
                    std::string count = x.substr(2);
                    canvas.categoriesLeftOpponent = std::stoi(count) + 1;
                }
                if (x[0] == 'v' && x[1] == ':'){
                    gamestate = waitingstate;
                    waitingWindow.messageText = waitingWindow.texts[1];
                    connected = false;
                    // Close the socket properly before reconnecting
                    network.closeSocket();
                    messageBuffer.clear();
                }
                if (x[0] == 'd' && x[1] == ':'){
                    gamestate = waitingstate;
                    waitingWindow.messageText = waitingWindow.texts[2];
                    connected = false;
                    // Close the socket properly before reconnecting
                    network.closeSocket();
                    messageBuffer.clear();
                }
                if (x[0] == '('){
                    canvas.aiPredictedText = x;
                    network.imagereceived = true;
                }
            }
        }
    }
    RaylibCloseWindow();
    network.shutDown();
    return 0;
}
