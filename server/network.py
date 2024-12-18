import socket
import threading
import queue
from PIL import Image
import io
import images

class Client:
    def __init__(self, client_id, model, processor, connection, address):
        self.id = client_id
        self.q = queue.Queue()
        self.should_run = threading.Event()
        self.should_run.set()  # Start in running state
        self.model = model
        self.processor = processor
        self.connection = connection
        self.address = address

    def send(self,clients):
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
            print(f"analyzing image from client {self.id}")
            score = images.analyze_images(self.model, self.processor, self.id)

            # Send the score back to the client
            score_message_self = (f"/" +str(score)).encode()
            score_message_other = (f"|" + str(score)).encode()
            for client in clients:
                if client == self:
                    client.connection.sendall(score_message_self)
                    client.connection.sendall(b"&")
                else:
                    client.connection.sendall(score_message_other)

    def recv(self):
        START_DELIMITER = b'<IMAGE_START>'
        END_DELIMITER = b'<IMAGE_END>'

        # Set timeout on the connection socket
        self.connection.settimeout(1.0)

        while self.should_run.is_set():
            try:
                image_data = b''
                while self.should_run.is_set():
                    try:
                        chunk = self.connection.recv(1024)
                        if chunk == b'&':
                            print("REQQIE BABIE WOOOO")
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
                    except socket.timeout:
                        continue
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
            if not chunk:
                break
        try:
            self.connection.close()
        except:
            pass
        print("hello 2")


def main(model, processor):
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
                    client = Client(len(clients), model, processor, connection, address)
                    clients.append(client)

                    recv_thread = threading.Thread(
                        target=client.recv,
                        daemon=True
                    )
                    send_thread = threading.Thread(
                        target=client.send,
                        args=(clients,),
                        daemon=True
                    )
                    client.connection.sendall(b"&")
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
        server_should_run.clear()
        for client in clients:
            client.should_run.clear()
        for client in clients:
            client.q.put(None)
        for t in threads:
            print("joining...")
            t.join()
        
