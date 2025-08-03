import socket


class UDPSender:
    def __init__(self, host="127.0.0.1", port=5005):
        self.address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: str):
        self.sock.sendto(message.encode(), self.address)
