import socket
import threading


class Server:

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.users = dict()

    def run(self):
        socket_server = self.create_server()

        while True:
            socket_conn, address = socket_server.accept()

            try:
                socket_conn.sendall('username'.encode('utf-8'))
                user_name = socket_conn.recv(1024)

                if self.users.get(socket_conn) is None:
                    self.users[socket_conn] = user_name.decode('utf-8')
                    connected = ' Connection established '.center(135, '-') + '\n\n'
                    socket_conn.send(connected.encode('utf-8'))

                threading.Thread(target=self.listening_users, args=(socket_conn,)).start()

            except ConnectionResetError:
                pass

    def create_server(self) -> socket.socket:
        socket_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_server.bind((self.ip, self.port))
        socket_server.listen(3)

        print('Server is running')

        return socket_server

    def listening_users(self, user_socket: socket.socket):
        while self.users:

            try:
                data = user_socket.recv(1024)
                print(data)

                if not data:
                    break

                self.send_msg_to_all(data=data, user_socket=user_socket)

            except ConnectionResetError:
                disconnected = f'[ *** LEFT THE CHAT *** ]'.encode('utf-8')
                self.send_msg_to_all(data=disconnected, user_socket=user_socket)

                del self.users[user_socket]
                user_socket.close()
                break

        user_socket.close()

    def send_msg_to_all(self, data: bytes, user_socket: socket.socket):
        for user in self.users:
            if user != user_socket:
                user.sendall(f"{self.users.get(user_socket)}: {data.decode('utf-8')}\n".encode('utf-8'))


if __name__ == '__main__':
    server = Server('127.0.0.1', 6666)
    server.run()
