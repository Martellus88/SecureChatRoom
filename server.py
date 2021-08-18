import socket
import threading


class Server:

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.users = {}

    def run(self):
        socket_server = self.create_server()

        while True:
            socket_conn, address = socket_server.accept()
            print(f'{address} is connected')

            user_name = socket_conn.recv(1024)

            if not self.users.get(socket_conn):
                self.users[socket_conn] = user_name.decode('utf-8')
                socket_conn.send('Соединение установленное'.encode('utf-8'))

                threading.Thread(target=self.listening_users, args=(socket_conn,)).start()

    def create_server(self):
        socket_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind((self.ip, self.port))
        socket_server.listen(3)

        print('Server is running')

        return socket_server


    def listening_users(self, user_socket: socket.socket):
        while True:
            try:
                data = user_socket.recv(1024)
                print(data)
            except ConnectionResetError:
                del self.users[user_socket]
                user_socket.shutdown(socket.SHUT_RDWR)
                user_socket.close()
                break

            if data:
                self.send_msg_to_all(data=data, user_socket=user_socket)

    def send_msg_to_all(self,data: bytes, user_socket: socket.socket):
        for user in self.users:
            if user != user_socket:
                user.sendall(f"{self.users.get(user_socket)}: {data}".encode('utf-8'))


if __name__ == '__main__':
    server = Server('127.0.0.1', 6666)
    server.run()
