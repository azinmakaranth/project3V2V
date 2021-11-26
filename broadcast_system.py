import argparse
import json
import socket
import threading
import time

from sensor import Sensor

broadcast_port = 33341
pair_list = {}


class HostConfigure:
    def __init__(self, hostaddress, port):
        self.host = hostaddress
        self.port = port


def peer_list_updater(BPORT):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 33341))
    index = 1
    print(pair_list)
    print([(pair_list[i].host, pair_list[i].port) for i in pair_list])
    while True:
        data = client.recvfrom(1024)
        print(data)
        decoded_data = json.loads(data[0].decode('utf-8'))
        print(decoded_data)
        print(f'testing pair -  {[(pair_list[key].host, pair_list[key].port) for key in list(pair_list)]}')
        flag = [decoded_data['host'] == pair_list[key].host and decoded_data['port'] == pair_list[key].port for key in
                list(pair_list)]
        print(flag)
        if any(flag):
            print('already exist')
            pass
        else:
            pair_list[index] = HostConfigure(decoded_data['host'], decoded_data['port'])
            index += 1
        print([(pair_list[i].host, pair_list[i].port) for i in pair_list])


def server_side(host, BPORT, LPORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = {'host': host, 'port': LPORT}
    encode_data = json.dumps(message, indent=2).encode('utf-8')
    while True:
        server.sendto(encode_data, ('<broadcast>', BPORT))
        time.sleep(5)


def information_listener(host, LPORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(host, LPORT)
    server.bind((host, LPORT))
    # server.setblocking(False)
    server.listen(5)
    while True:
        conn, addr = server.accept()
        conn.setblocking(False)
        try:
            recv_data = conn.recv(1024)
            decoded_data = recv_data.decode('utf-8')
            print(f'received data : {decoded_data} from {addr}')
        except Exception as e:
            pass
            # print(f'error receiving {e} {addr}')


def send_information():
    while True:
        for peer in pair_list.keys():
            peerHost = pair_list[peer].host
            peerPort = int(pair_list[peer].port)
            if host == peerHost and args.listen_port == peerPort:
                continue
            peer = Sensor()
            message = "sample"
            peer.send_messages(peerHost, peerPort, message)
        time.sleep(5)


my_parser = argparse.ArgumentParser(description='command to execute the ./server script')
my_parser.add_argument('--listen_port', help='listening_port', required=True)
args = my_parser.parse_args()
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
pair_list[0] = HostConfigure(host, args.listen_port)
serverThread = threading.Thread(target=server_side, args=(host, broadcast_port, args.listen_port,))
peerThread = threading.Thread(target=peer_list_updater, args=(broadcast_port,))
infoThread = threading.Thread(target=information_listener, args=(host, int(args.listen_port),))
sensorThread = threading.Thread(target=send_information)

serverThread.start()
peerThread.start()

time.sleep(5)
infoThread.start()

sensorThread.start()
