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
    int bytesReceived = recv(output, buffer, sizeof(buffer), 0);
    if (bytesReceived == SOCKET_ERROR) {
        if (WSAGetLastError() != WSAEWOULDBLOCK) {
//            std::cerr << "recv() failed: " << WSAGetLastError() << "\n";
            return "";
        }
    } else if (bytesReceived == 0) {
        // Connection closed by server
        std::cerr << "Server closed connection\n";
        return "";
    } else {
        std::string str(buffer, bytesReceived);
        return str;
    }
    return "";
}

bool Network::sendData(std::string s) {
    int message = send(output, s.c_str(), static_cast<int>(s.size()), 0);
    if (message == SOCKET_ERROR) {
        std::cerr << "send() failed: " << WSAGetLastError() << "\n";
        return false;
    }
    return true;
}

void Network::sendLocalImageData(std::string fileName, std::string password) {
    std::ifstream file(fileName, std::ios::binary);
    if (!file) {
        std::cerr << "Failed to open file: " << fileName << "\n";
        return;
    }
    std::vector<char> buffer((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();
    std::cout << "Sending image: " << fileName << " (" << buffer.size() << " bytes)" << std::endl;
    const std::string header = "CLIENTPNG:";
    std::vector<char> packet;
    packet.insert(packet.end(), header.begin(), header.end());
    packet.insert(packet.end(), buffer.begin(), buffer.end());
    size_t totalSent = 0;
    size_t packetSize = packet.size();
    while (totalSent < packetSize) {
        int sent = send(output, packet.data() + totalSent, static_cast<int>(packetSize - totalSent), 0);
        if (sent == SOCKET_ERROR) {
            std::cerr << "send() failed at offset " << totalSent << ": " << WSAGetLastError() << "\n";
            return;
        }
        totalSent += sent;
        std::cout << "Sent " << sent << " bytes, total: " << totalSent << "/" << packetSize << std::endl;
    }
    const std::string endMarker = "CLIENTPNG_END:";
    int message = send(output, endMarker.c_str(), static_cast<int>(endMarker.size()), 0);
    if (message == SOCKET_ERROR) {
        std::cerr << "send() failed for END marker: " << WSAGetLastError() << "\n";
    } else {
        std::cout << "Image sent successfully!" << std::endl;
    }
    imagereceived = false;
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
    output = socket(AF_INET, SOCK_STREAM, 0);
    if (output == INVALID_SOCKET) {
        std::cerr << "Error creating socket: " << WSAGetLastError() << "\n";
        return 1;
    }

    // Set socket to non-blocking mode
    u_long mode = 1;
    ioctlsocket(output, FIONBIO, &mode);

    return 0;
}

void Network::shutDown() {
    closesocket(output);
    WSACleanup();
}

int Network::init(std::string ip, int port) {
    serverMessage.sin_family = AF_INET;
    if (port == 1) {
        serverMessage.sin_port = htons(54000);
    }
    else if (port == 2) {
        std::cout << "chosen port 2\n";
        serverMessage.sin_port = htons(54001);
    } else {
        return 1;
    }

    if (inet_pton(AF_INET, ip.c_str(), &serverMessage.sin_addr) != 1) {
        std::cerr << "Invalid address. inet_pton failed\n";
        return 1;
    }
    return 0;
}

int Network::connectToServer() {
    int result = connect(output, (sockaddr*)&serverMessage, sizeof(serverMessage));
    if (result == SOCKET_ERROR) {
        int error = WSAGetLastError();
        if (error != WSAEWOULDBLOCK) {
            std::cerr << "connect() failed: " << error << "\n";
            return 1;
        }
    }
    return 0;
}
void Network::closeSocket() {
    if (output != INVALID_SOCKET) {
        closesocket(output);
        output = INVALID_SOCKET;
    }

}
