//
// Created by benra on 6/4/2024.
//

#include "Network.h"
#include <iostream>
#include <vector>
#include "cmath"
#include "fstream"
std::string Network::receiveData() {
    memset(buffer, 0, sizeof(buffer));
    int bytesReceived = recvfrom(output, buffer, sizeof(buffer), 0, (sockaddr*)&serverResponse, &serverResponseSize);
    if (bytesReceived == SOCKET_ERROR) {
        if (WSAGetLastError() != WSAEWOULDBLOCK) {
//            std::cerr << "recvfrom() failed: " << WSAGetLastError() << "\n";
            return "";
        }
    } else {
        std::string str(buffer, sizeof(buffer));
        return str;
    }
    return "";
}
void Network::sendData(std::string s) {
    int message = sendto(output, s.c_str(), static_cast<int>(s.size()) + 1, 0, (sockaddr*)&serverMessage, sizeof(serverMessage));
    if (message == SOCKET_ERROR) {
        std::cerr << "sendto() failed: " << WSAGetLastError() << "\n";
    }
}
void Network::sendLocalImageData(std::string fileName, std::string password) {
    std::ifstream file(fileName, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open file: " << fileName << "\n";
        return;
    }

    std::vector<char> buffer((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    const std::string header = "CLIENTPNG:"+password+":";
    const std::string endMarker = "CLIENTPNG_END:"+password;
    const size_t CHUNK_SIZE = 20 * 1024;  // 20 KB

    size_t totalSize = buffer.size();
    size_t offset = 0;

    while (offset < totalSize) {
        size_t chunkLen = std::min(CHUNK_SIZE, totalSize - offset);
        std::vector<char> packet;
        packet.insert(packet.end(), header.begin(), header.end());
        packet.insert(packet.end(), buffer.begin() + offset, buffer.begin() + offset + chunkLen);

        int message = sendto(output, packet.data(), static_cast<int>(packet.size()), 0,
                             (sockaddr*)&serverMessage, sizeof(serverMessage));
        if (message == SOCKET_ERROR) {
            std::cerr << "sendto() failed at chunk offset " << offset << ": " << WSAGetLastError() << "\n";
            return;
        }

        offset += chunkLen;
    }

    // Send final "CLIENTPNG_END" message
    int message = sendto(output, endMarker.c_str(), static_cast<int>(endMarker.size()), 0,
                         (sockaddr*)&serverMessage, sizeof(serverMessage));
    if (message == SOCKET_ERROR) {
        std::cerr << "sendto() failed for END marker: " << WSAGetLastError() << "\n";
    }
}

int Network::startup() {
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        std::cerr << "WSAStartup failed: " << iResult << "\n";
        return 1;
    }
    return 0;
}
int Network::createSocket() {
    output = socket(AF_INET, SOCK_DGRAM, 0);
    if (output == INVALID_SOCKET) {
        std::cerr << "Error creating socket: " << WSAGetLastError() << "\n";
        return 1;
    }
    u_long mode = 1;
    ioctlsocket(output, FIONBIO, &mode);
    serverResponseSize = sizeof(serverResponse);
    return 0;
}
void Network::shutDown() {
    closesocket(output);
    WSACleanup();
}
int Network::init(std::string ip, int port){
    serverMessage.sin_family = AF_INET;
    if (port == 1){
        serverMessage.sin_port = htons(54000);
    }
    else if (port == 2) {
        std::cout<<"chosen port 2\n";
        serverMessage.sin_port = htons(54001);
    }else {
        return 1;
    }

    if (inet_pton(AF_INET, ip.c_str(), &serverMessage.sin_addr) != 1) {
        std::cerr << "Invalid address. inet_pton failed\n";
        return 1;
    }
    return 0;
}