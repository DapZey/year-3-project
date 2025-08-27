// Network.h
#ifndef NETWORK_H
#define NETWORK_H

#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>

#pragma comment(lib, "ws2_32.lib")

class Network {
private:
    WSADATA wsaData;
    SOCKET output;
    sockaddr_in serverMessage;
    char buffer[30000];
    int iResult;
    std::string receiveBuffer;  // NEW: Buffer to accumulate received data

public:
    bool imagereceived = true;

    int startup();
    int createSocket();
    int init(std::string ip, int port);
    int connectToServer();  // NEW: Connect to TCP server
    std::string receiveData();
    bool sendData(std::string s);
    void sendLocalImageData(std::string fileName, std::string password);
    void shutDown();
    void closeSocket();
};

#endif
