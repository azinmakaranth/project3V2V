import socket

# Suggest a better name for this class.
class p2p:
    def __init__(self):
        self.speed = 0
        self.proximity = 0
        sock = None

    def send_messages(self, host, port, send_port, data):
        server_address = (host, port)
        flag = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        print(host, send_port)
        self.sock.bind((host, send_port))
        self.sock.connect_ex(server_address)
        try:
            self.sock.send(data.encode('utf-8'))
            self.sock.close()
            return flag
        except Exception as e:
            print(f'{e} {server_address}')
            self.sock.close()
            return False