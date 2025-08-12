#include <iostream>
#include "raylib.h"
#include "Network.h"`
#include "Canvas.h"
#include "algorithm"
int main() {
    const int screenWidth = 1290;
    const int screenHeight = 960;
    int port;
    std::cin>> port;
    std::string password;
    if (port == 1){
        password = "c1";
    }
    else {
        password = "c2";
    }
    InitWindow(screenWidth, screenHeight, "AIV2");
    SetTargetFPS(500);
    Network network;
    Canvas canvas(screenWidth,screenHeight);
    network.startup();
    int connectionTry = 1;
    connectionTry = network.init("127.0.0.1", 1);
    while (!WindowShouldClose())
    {
        if (connectionTry == 0){
            network.createSocket();
            connectionTry = 2;
            network.sendData("req"+password);
        }
        canvas.drawCanvas();
        if (canvas.ReadyToSendImageInput && network.imagereceived){
            canvas.ReadyToSendImageInput = false;
            network.imagereceived = false;
            network.sendLocalImageData("my_amazing_texture_painting.png", password);
        }
        std::string x= network.receiveData();
        if (!x.empty()){
            std::cout<<x<<"\n";
            network.imagereceived = true;
            if (x[0] == 'c' && x[1] == ':'){
                x.erase(0,2);
                canvas.category = x;
                canvas.categoriesLeft--;
            }
            if (x[0] == 'o' && x[1] == 's'){
                canvas.categoriesLeftOpponent--;
            }
            x = "";
        }
    }
    RaylibCloseWindow();
    network.shutDown();
    return 0;
}
