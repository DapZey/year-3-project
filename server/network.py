import socket
import threading
import queue
from PIL import Image
import io
import images

class Client:
    def __init__(self, client_id):
        self.id = client_id
        self.q = queue.Queue()
        self.should_run = threading.Event()
        self.should_run.set()  # Start in running state

    def send(self):
        while self.should_run.is_set():
            try:
                # Add timeout to queue.get() so we can check should_run
                image_data = self.q.get(timeout=1.0)
                if image_data is None:
                    break

                print(f"Received data size: {len(image_data)}")
                with open(f"client{self.id}.png", 'wb') as f:
                    f.write(image_data)
                image = Image.open(io.BytesIO(image_data))
                image = image.convert('RGBA')
            except queue.Empty:
                continue  # Timeout occurred, check should_run again
            except Exception as e:
                print(f"Error processing image: {e}")
            self.q.task_done()

    def recv(self, connection, address):
        START_DELIMITER = b'<IMAGE_START>'
        END_DELIMITER = b'<IMAGE_END>'

        while self.should_run.is_set():
            try:
                image_data = b''
                while self.should_run.is_set():
                    chunk = connection.recv(1024)
                    if not chunk:
                        break

                    if START_DELIMITER in chunk:
                        image_data = chunk[chunk.find(START_DELIMITER) + len(START_DELIMITER):]
                        continue

                    if END_DELIMITER in chunk:
                        image_data += chunk[:chunk.find(END_DELIMITER)]
                        print("Server received complete image")
                        self.q.put(image_data)
                        image_data = b''  # Reset buffer
                        continue

                    image_data += chunk

            except Exception as e:
                print(f"Error receiving data: {e}")
                break

            if not chunk:
                break


def main():
    images.freeze_support()
    model = images.CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = images.CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    images.analyze_images(model,processor,0)
    server_should_run = threading.Event()
    server_should_run.set()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8000))
    server_socket.listen(2)

    clients = []
    threads = []

    def console_monitor():
        while server_should_run.is_set():
            if input().strip().lower() == 'exit':
                print("Shutting down server...")
                server_should_run.clear()  # Signal main loop to stop
                for c in clients:
                    c.should_run.clear()  # Signal all clients to stop
                break

    console_thread = threading.Thread(target=console_monitor, daemon=True)
    console_thread.start()

    try:
        while server_should_run.is_set():
            server_socket.settimeout(1.0)
            try:
                connection, address = server_socket.accept()
                print(f"Connection from {address}")
                if len(clients) >= 2:
                    print(f"Rejecting connection from {address}: server full")
                    connection.send(b"Server is full")
                    connection.close()
                    continue
                else:
                    client = Client(len(clients))
                    clients.append(client)

                    recv_thread = threading.Thread(
                        target=client.recv,
                        args=(connection, address),
                        daemon=True
                    )
                    send_thread = threading.Thread(
                        target=client.send,
                        daemon=True
                    )

                    recv_thread.start()
                    send_thread.start()
                    threads.append(recv_thread)
                    threads.append(send_thread)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server_should_run.clear()
        for client in clients:
            client.should_run.clear()
    finally:
        server_socket.close()
        for client in clients:
            client.q.put(None)
        for t in threads:
            print("joining...")
            t.join()

