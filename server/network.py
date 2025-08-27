import socket
import io
from PIL import Image
from TEST import predictclientimage, categories
import random
import time
import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 54000))
server_socket.listen(2)
server_socket.setblocking(False)

# Client connections
client1_socket = None
client2_socket = None

# Passwords
client1pwd = "c1"
client2pwd = "c2"

# Buffers for each client
image_buffer1 = bytearray()
image_buffer2 = bytearray()

# categories = [ "house", "car", "tree", "smiley face",
#                "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

client1categories = categories.copy()
client2categories = categories.copy()

client1currentcategory = ""
client2currentcategory = ""


def selectCategoryForClient(categoryList):
    category = random.choice(categoryList)
    categoryList.remove(category)
    print(category)
    return category


client1currentcategory = selectCategoryForClient(client1categories)
client2currentcategory = selectCategoryForClient(client2categories)

address_tuple = None
c1tuple = None
c2tuple = None


def recv():
    global address_tuple, image_buffer1, image_buffer2, client1currentcategory, client2currentcategory, client2categories, client1categories
    global c1tuple, c2tuple
    global client1_socket, client2_socket

    reset_globals_flag = False

    # Handle new connections
    try:
        ready_to_read, _, _ = select.select([server_socket], [], [], 0.2)
        if server_socket in ready_to_read:
            client_socket, client_address = server_socket.accept()
            client_socket.setblocking(False)

            if client1_socket is None:
                client1_socket = client_socket
                c1tuple = client_address
                send("c:" + str(client1currentcategory), client1_socket)
                send("t:" + str(len(client1categories)), client1_socket)
                send("w:", client1_socket)
            elif client2_socket is None:
                client2_socket = client_socket
                c2tuple = client_address
                send("c:" + str(client2currentcategory), client2_socket)
                send("t:" + str(len(client2categories)), client2_socket)
                send("s:", client1_socket)
                send("s:", client2_socket)
            else:
                send("err conn", client_socket)
    except BlockingIOError:
        pass

    # Handle messages from existing clients
    clients_to_check = []
    if client1_socket:
        clients_to_check.append((client1_socket, "client1"))
    if client2_socket:
        clients_to_check.append((client2_socket, "client2"))

    for client_socket, client_name in clients_to_check:
        try:
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.2)
            if client_socket in ready_to_read:
                message = client_socket.recv(30000)
                if not message:  # Client disconnected
                    print(f"{client_name} disconnected")
                    if client_socket == client1_socket:
                        if client2_socket:
                            send("v:", client2_socket)
                    else:
                        if client1_socket:
                            send("v:", client1_socket)
                    reset_globals_flag = True
                    continue

                address_tuple = client_socket.getpeername()

                # Handle different message types
                if message.startswith(b'req'):
                    # This is handled in the connection acceptance above
                    pass

                elif message.startswith(b'CLIENTPNG:'):
                    # Start of image data
                    header_len = len(b'CLIENTPNG:')
                    image_data = message[header_len:]

                    if client_socket == client1_socket:
                        image_buffer1 = bytearray(image_data)
                        print(f"Started receiving image for client1: {len(image_data)} bytes")
                    elif client_socket == client2_socket:
                        image_buffer2 = bytearray(image_data)
                        print(f"Started receiving image for client2: {len(image_data)} bytes")

                    # Continue receiving until we get the end marker
                    while True:
                        try:
                            ready_to_read, _, _ = select.select([client_socket], [], [], 0.2)
                            if client_socket in ready_to_read:
                                more_data = client_socket.recv(30000)
                                if not more_data:
                                    break

                                # Check if this chunk contains the end marker
                                if b'CLIENTPNG_END:' in more_data:
                                    # Find where the end marker starts
                                    end_pos = more_data.find(b'CLIENTPNG_END:')
                                    # Add data before the end marker to image
                                    if end_pos > 0:
                                        if client_socket == client1_socket:
                                            image_buffer1 += more_data[:end_pos]
                                        else:
                                            image_buffer2 += more_data[:end_pos]

                                    print(
                                        f"Image complete for {client_name}: {len(image_buffer1 if client_socket == client1_socket else image_buffer2)} bytes")

                                    # Process the complete image
                                    if client_socket == client1_socket:
                                        with open("received_client1.png", "wb") as f:
                                            f.write(image_buffer1)
                                        print("Saved image for client1")
                                        try:
                                            test_image = Image.open("received_client1.png")
                                            test_image.verify()
                                            x = predictclientimage("received_client1.png")
                                            if (x[0] == client1currentcategory and x[1] > 0.1):
                                                if len(client1categories) == 0:
                                                    send("v:", client1_socket)
                                                    send("d:", client2_socket)
                                                    # Add a small delay to ensure messages are sent before closing
                                                    time.sleep(0.1)
                                                    resetGlobals()
                                                else:
                                                    client1currentcategory = selectCategoryForClient(client1categories)
                                                    send("c:" + str(client1currentcategory), client_socket)
                                                    send("o:" + str(len(client1categories)), client2_socket)
                                                    send("o:" + str(len(client2categories)), client1_socket)
                                                    send("t:" + str(len(client1categories)), client1_socket)
                                            send(str(x), client_socket)
                                        except Exception as e:
                                            print("Display failed for client1:", e)
                                        image_buffer1.clear()
                                    else:
                                        with open("received_client2.png", "wb") as f:
                                            f.write(image_buffer2)
                                        print("Saved image for client2")
                                        try:
                                            test_image = Image.open("received_client2.png")
                                            test_image.verify()
                                            x = predictclientimage("received_client2.png")
                                            if (x[0] == client2currentcategory and x[1] > 0.1):
                                                if len(client2categories) == 0:
                                                    send("v:", client2_socket)
                                                    send("d:", client1_socket)
                                                    # Add a small delay to ensure messages are sent before closing
                                                    time.sleep(0.1)
                                                    resetGlobals()
                                                else:
                                                    client2currentcategory = selectCategoryForClient(client2categories)
                                                    send("c:" + str(client2currentcategory), client_socket)
                                                    send("o:" + str(len(client2categories)), client1_socket)
                                                    send("o:" + str(len(client1categories)), client2_socket)
                                                    send("t:" + str(len(client2categories)), client2_socket)
                                            send(str(x), client_socket)
                                        except Exception as e:
                                            print("Display failed for client2:", e)
                                        image_buffer2.clear()
                                    break
                                else:
                                    # More image data, keep accumulating
                                    if client_socket == client1_socket:
                                        image_buffer1 += more_data
                                    else:
                                        image_buffer2 += more_data
                                    print(f"Continuing to receive image for {client_name}: +{len(more_data)} bytes")
                            else:
                                # No more data available right now, continue outer loop
                                break
                        except BlockingIOError:
                            break

                elif message.startswith(b'CLIENTPNG_END:'):
                    # This should now be handled above
                    pass

                else:
                    # Check if this is continuation of image data (binary data with no recognized header)
                    if (len(image_buffer1) > 0 and client_socket == client1_socket) or \
                            (len(image_buffer2) > 0 and client_socket == client2_socket):
                        # This is likely continuation of image data
                        if client_socket == client1_socket:
                            image_buffer1 += message
                            print(
                                f"Continuing image data for client1: +{len(message)} bytes, total: {len(image_buffer1)}")
                        else:
                            image_buffer2 += message
                            print(
                                f"Continuing image data for client2: +{len(message)} bytes, total: {len(image_buffer2)}")
                    else:
                        print("Received other message:", message)

        except BlockingIOError:
            pass
        except ConnectionResetError as e:
            print(f"{client_name} connection reset")
            if client_socket == client1_socket:
                if client2_socket:
                    send("v:", client2_socket)
            else:
                if client1_socket:
                    send("v:", client1_socket)
            reset_globals_flag = True
        except Exception as e:
            print(f"Error with {client_name}: {e}")
            if client_socket == client1_socket:
                if client2_socket:
                    send("v:", client2_socket)
            else:
                if client1_socket:
                    send("v:", client1_socket)
            reset_globals_flag = True

    # Call resetGlobals at the end if flag is set
    if reset_globals_flag:
        resetGlobals()


def send(response, client_socket):
    if client_socket is not None:
        try:
            # Wrap message with | delimiters
            message = f"|{response}|".encode()
            client_socket.send(message)
            print("Sent:", response)
        except Exception as e:
            print(f"Failed to send message: {e}")


def resetGlobals():
    global address_tuple, categories, image_buffer1, image_buffer2, client1currentcategory, client2currentcategory, client2categories, client1categories, c1tuple, c2tuple
    global client1_socket, client2_socket

    c1tuple = None
    c2tuple = None

    # Close existing connections
    if client1_socket:
        try:
            client1_socket.close()
        except:
            pass
        client1_socket = None
    if client2_socket:
        try:
            client2_socket.close()
        except:
            pass
        client2_socket = None

    image_buffer1.clear()
    image_buffer2.clear()
    client1categories = categories.copy()
    client2categories = categories.copy()
    client1currentcategory = selectCategoryForClient(client1categories)
    client2currentcategory = selectCategoryForClient(client2categories)
    address_tuple = None

# Main loop - you would call recv() repeatedly in your main loop
# while True:
#     recv()
#     time.sleep(0.01)  # Small delay to prevent excessive CPU usage
