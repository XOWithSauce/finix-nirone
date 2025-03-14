import os
import socket
import sys
import json

class BSDClient():
    def __init__(self) -> None:
        self.LABELS = ["Polyester", "Cotton", "Wool"]
        self.SOCK_POST = '/tmp/model-ipc-post.socket'
        if not os.path.exists(self.SOCK_POST):
            print(f"WARNING: File {self.SOCK_POST} doesn't exist")

        self.socket_post = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def local_inference(self, data: list):
        print("connecting to socket")
        try:
            print("SOCKET FILENO: ", self.socket_post.fileno())
            self.socket_post.connect('/tmp/model-ipc-post.socket')
        except Exception as e:
            print("Socket already connected: ", e)
            
        decoded_labels = ""
        serialized_data = json.dumps(data)
        self.socket_post.sendall(serialized_data.encode())
        print("Sending bytes: ", sys.getsizeof(serialized_data.encode()))
        print("Wait for response")
        result = self.socket_post.recv(1024).decode()
        print(f'Received bytes: {repr(result)}')
        try:
            parsed_data = json.loads(result)
            print(type(parsed_data))
            try:
                decoded_labels = self.decode_labels(parsed_data[0])
            except Exception as e:
                print("Failed to decode labels from prediction: ", e)
        except Exception as e:
            print("Failed to load json object: ", e)
        return decoded_labels
    
    def decode_labels(self, predicted_data):
        # Convert probabilities to percentages and sort them in descending order
        percentages = [round(prob * 100, 1) for prob in predicted_data]  # Round to one decimal place
        sorted_data = sorted(zip(percentages, self.LABELS), reverse=True)

        # Format the string
        formatted_string = ""
        for percentage, label in sorted_data:
            formatted_string += f"{label}: {percentage}%\n"
            
        print("FORMATTED: \n", formatted_string)
        return formatted_string