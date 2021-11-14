import socket
import threading
import os
import time
from hashlib import sha256

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP


class Server:
    MAX_CLIENTS = 2

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.socket_server = None

        self.__ssk = None

        self.users = dict()

    def run(self):
        self.create_server()

        # self.__ssk = os.urandom(32) #?

        while True:

            socket_conn, address = self.socket_server.accept()

            try:
                user_name = socket_conn.recv(1024)

                if self.users.get(socket_conn) is None and len(self.users) < self.MAX_CLIENTS:
                    if self.__ssk is None:
                        self.__ssk = os.urandom(32)
                    self.__handshake(socket_conn=socket_conn)
                    self.users[socket_conn] = user_name


                    connected = ' Connection established '.center(135, '-') + '\n\n'
                    socket_conn.send(connected.encode('utf-8'))

                    threading.Thread(target=self.listening_users, args=(socket_conn,)).start()
                if len(self.users) == self.MAX_CLIENTS:
                    self.__ssk = None
            except ConnectionResetError as e:
                print(e, type(e))

    def create_server(self):
        self.socket_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(self.MAX_CLIENTS)

        print('Server is running')

    def __handshake(self, socket_conn):
        pub_key = socket_conn.recv(2048)
        time.sleep(0.1)
        hash_ssk = sha256(self.__ssk).digest()
        encrypt_ssk = self.crypt_session_key(client_pub_key=pub_key)
        socket_conn.send(encrypt_ssk + b'&-^*' + hash_ssk)

    def listening_users(self, user_socket):
        while True:
            try:
                data = user_socket.recv(2048)
                if not data:
                    break
                self.send_msg_to_all(data=data, user_socket=user_socket)
            except ConnectionResetError:
                disconnected = '[ *** LEFT THE CHAT *** ]\n'.encode('utf-8')
                self.send_msg_to_all(data=disconnected, user_socket=user_socket)

                del self.users[user_socket]
                user_socket.close()
                break

        user_socket.close()

    def send_msg_to_all(self, data: bytes, user_socket):
        for user in self.users:
            if user != user_socket:
                user.sendall(self.users.get(user_socket) + b'&??*' + data)

    def crypt_session_key(self, client_pub_key):
        try:
            user_key = RSA.import_key(client_pub_key)
            cipher_rsa = PKCS1_OAEP.new(user_key)
            encrypt_session_key = cipher_rsa.encrypt(self.__ssk)
            return encrypt_session_key
        except ValueError as e:
            print('Hacking attempt!', e)
            self.socket_server.close()
            exit()

if __name__ == '__main__':
    server = Server('127.0.0.1', 6666)
    server.run()
