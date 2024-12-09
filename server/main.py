import socket
import threading
import queue
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8000))
serversocket.listen(2)

q = queue.Queue()


def send():
    while True:
        image_data = q.get()
        if image_data is None:
            break

        try:
            print(f"Received data size: {len(image_data)}")

            # Save the image
            with open('client1.png', 'wb') as f:
                f.write(image_data)

            # Display the image
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGBA')
            # image_array = np.array(image)
            # plt.imshow(image_array)
            # plt.show()
        except Exception as e:
            print(f"Error processing image: {e}")
        q.task_done()


def recv():
    START_DELIMITER = b'<IMAGE_START>'
    END_DELIMITER = b'<IMAGE_END>'

    while True:
        connection, address = serversocket.accept()
        print(f"Connection from {address}")

        try:
            image_data = b''
            while True:
                chunk = connection.recv(1024)
                if not chunk:
                    break

                if START_DELIMITER in chunk:
                    image_data = chunk[chunk.find(START_DELIMITER) + len(START_DELIMITER):]
                    continue

                if END_DELIMITER in chunk:
                    image_data += chunk[:chunk.find(END_DELIMITER)]
                    print("Server received complete image")
                    q.put(image_data)
                    image_data = b''  # Reset buffer
                    continue

                image_data += chunk

        except Exception as e:
            print(f"Error receiving data: {e}")

recv_thread = threading.Thread(target=recv, daemon=True)
send_thread = threading.Thread(target=send, daemon=True)

recv_thread.start()
send_thread.start()

# Join threads (not strictly necessary for daemon threads)
recv_thread.join()
send_thread.join()
