import os
import socket
import json
import asyncio
from loaded_model import TFLiteModel

class BSDServer():
    def __init__(self) -> None:
        self.model = TFLiteModel("model.tflite")
        self.SOCK_POST = '/tmp/model-ipc-post.socket'
        if not os.path.exists(self.SOCK_POST):
            print(f"WARNING: File {self.SOCK_POST} doesn't exist")

        self.socket_post = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        print(f"Model IPC Socket starting at '{self.SOCK_POST}'")
        print(f"Model parameters:\n{self.model.input_details}\n{self.model.output_details}\n-----")

    async def main_loop(self):
        self.socket_post.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_post.bind(self.SOCK_POST)
        self.socket_post.listen(0)
        print("succesfully bound to socket")
        while True:
            await asyncio.sleep(0.6)
            print("Waiting client...")
            conn, addr = self.socket_post.accept()
            print("Client connected")
            while True:
                await asyncio.sleep(1)
                print("Waiting for data")
                received_data = conn.recv(16384)
                received_list = json.loads(received_data.decode())
                print(f"Received data: {received_list}")
                result = self.model.predict(received_list)
                print(result)
                print(type(result))
                serialized_data = json.dumps(result.tolist())
                print(serialized_data)
                print("Sending data:")
                conn.sendall(serialized_data.encode())

if __name__ == "__main__":
    app = BSDServer()
    asyncio.run(app.main_loop())