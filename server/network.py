import socket
import io
from PIL import Image
from TEST import predictclientimage
import random

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 54000))
server_socket.setblocking(False)

# Passwords
client1pwd = "c1"
client2pwd = "c2"

# Buffers for each client
image_buffer1 = bytearray()
image_buffer2 = bytearray()

categories = [ "house", "car", "tree", "smiley face",
               "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

client1categories =  [ "house", "car", "tree", "smiley face",
              "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

client2categories = [ "house", "car", "tree", "smiley face",
               "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

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
c2tuple= None
def recv():
    global address_tuple, image_buffer1, image_buffer2, client1currentcategory, client2currentcategory, client2categories, client1categories, c1tuple, c2tuple
    try:
        message, address = server_socket.recvfrom(30000)
        address_tuple = address
        if message.startswith(b'req'):
            if c1tuple == None:
                c1tuple = address_tuple
                send("c:"+str(client1currentcategory),c1tuple)
                send("t:" + str(len(client1categories)), c1tuple)
                send("w:",c1tuple)
            elif c2tuple == None:
                c2tuple = address_tuple
                send("c:" + str(client2currentcategory), c2tuple)
                send("t:" + str(len(client2categories)), c2tuple)
                send("s:", c1tuple)
                send("s:", c2tuple)
            else:
                send("err conn",address_tuple)

        if message.startswith(b'CLIENTPNG:'):
            try:
                # Extract password and chunk
                header, chunk_data = message.split(b':', 1)
            except ValueError:
                print("Malformed CLIENTPNG message")
                return

            if address_tuple == c1tuple:
                image_buffer1 += chunk_data
                print("Received chunk for client1")
            elif address_tuple == c2tuple:
                image_buffer2 += chunk_data
                print("Received chunk for client2")
            else:
                print(f"Invalid from addr")

        # End signal
        elif message.startswith(b'CLIENTPNG_END:'):

            if address_tuple == c1tuple:
                with open("received_client1.png", "wb") as f:
                    f.write(image_buffer1)
                print("Saved image for client1")
                try:
                    Image.open(io.BytesIO(image_buffer1))
                    x = predictclientimage("received_client1.png")
                    if (x[0] == client1currentcategory and x[1] > 0.1):
                        if len(client1categories) == 0:
                            send("v:", c1tuple)
                            send("d:", c2tuple)
                            resetGlobals()
                        else:
                            client1currentcategory = selectCategoryForClient(client1categories)
                            send("c:" + str(client1currentcategory), address_tuple)
                            send("o:" + str(len(client1categories)), c2tuple)
                            send("o:" + str(len(client2categories)), c1tuple)
                            send("t:" + str(len(client1categories)), c1tuple)
                    send(str(x), address_tuple)
                except Exception as e:
                    print("Display failed for client1:", e)
                image_buffer1.clear()

            elif address_tuple == c2tuple:
                with open("received_client2.png", "wb") as f:
                    f.write(image_buffer2)
                print("Saved image for client2")
                try:
                    Image.open(io.BytesIO(image_buffer2))
                    x = predictclientimage("received_client2.png")
                    if (x[0] == client2currentcategory and x[1] > 0.1):
                        if len(client2categories) == 0:
                            send("v:", c2tuple)
                            send("d:", c1tuple)
                            resetGlobals()
                        else:
                            client2currentcategory = selectCategoryForClient(client2categories)
                            send("c:" + str(client2currentcategory), address_tuple)
                            send("o:" + str(len(client2categories)), c1tuple)
                            send("o:" + str(len(client1categories)), c2tuple)
                            send("t:" + str(len(client2categories)), c2tuple)
                    send(str(x), address_tuple)
                except Exception as e:
                    print("Display failed for client2:", e)
                image_buffer2.clear()

            else:
                print(f"Invalid addr")

        else:
            print("Received other message:", message)

    except BlockingIOError:
        pass
    except ConnectionResetError as e:
        pass


def send(response, tuple):
    if tuple is not None:
        server_socket.sendto(response.encode(), tuple)
        print("Sent:", response)

def resetGlobals():
    global address_tuple,categories, image_buffer1, image_buffer2, client1currentcategory, client2currentcategory, client2categories, client1categories, c1tuple, c2tuple
    c1tuple = None
    c2tuple = None
    image_buffer1.clear()
    image_buffer2.clear()
    client1categories = categories.copy()
    client2categories = categories.copy()
    client1currentcategory = selectCategoryForClient(client1categories)
    client2currentcategory = selectCategoryForClient(client2categories)
    address_tuple = None
# Main loo
