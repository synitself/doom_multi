import socket
import pickle
from settings import SERVER_HOST, SERVER_PORT

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.addr = (self.host, self.port)
        self.initial_data = self.connect()

    def get_initial_data(self):
        return self.initial_data

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(e)
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(e)
            return None