#include <iostream>
#include "raylib.h"
#include "Network.h"`
#include "Canvas.h"
#include "algorithm"
#include "ConnectWindow.h"
#include "waitingWindow.h"
enum Gamestate{
    connectwindowstate,
    waitingstate,
    playingstate,
};
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
            if (connectWindow.getInput() == 1){
                int connectionTry = 1;
                connectionTry = network.init(connectWindow.text, 1);
                if (connectionTry == 0){
                    network.createSocket();
                    connectionTry = 2;
                    network.sendData("req");
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
        }
        std::string x= network.receiveData();
        if (!x.empty()){
            std::cout<<x<<"\n";
            network.imagereceived = true;
            if (x[0] == 'p'){
                network.sendData("ping");
            }
            if (x[0] == 'w' && x[1] == ':'){
                gamestate = waitingstate;
            }
            if (x[0] == 's' && x[1] == ':'){
                gamestate = playingstate;
            }
            if (x[0] == 'e' && x[1] == 'r'){
                gamestate = connectwindowstate;
            }
            if (x[0] == 'c' && x[1] == ':'){
                x.erase(0,2);
                canvas.category = x;
            }
            if (x[0] == 't' && x[1] == ':'){
                x.erase(0,2);
                canvas.categoriesLeft = std::stoi(x) + 1;
                //guessed correct
                canvas.ClearCanvas();
            }
            if (x[0] == 'o' && x[1] == ':'){
                x.erase(0,2);
                canvas.categoriesLeftOpponent = std::stoi(x) + 1;
            }
            if (x[0] == 'v' && x[1] == ':'){
                gamestate = waitingstate;
                waitingWindow.messageText = waitingWindow.texts[1];
            }
            if (x[0] == 'd' && x[1] == ':'){
                gamestate = waitingstate;
                waitingWindow.messageText = waitingWindow.texts[2];
            }

            if (x[0] == '('){
                canvas.aiPredictedText = x;
            }
            x = "";
        }
    }
    RaylibCloseWindow();
    network.shutDown();
    return 0;
}
