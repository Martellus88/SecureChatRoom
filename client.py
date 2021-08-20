import socket
import threading
from client_gui import Gui


class Client:

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.stop = False

        self.user_name = None
        self.client_socket = None
        self.msg = ''

        self.gui = Gui(self)

    def run(self):
        self.create_socket()
        self.gui.init_gui()

        listen_thread = threading.Thread(target=self.listen_server, daemon=True)
        listen_thread.start()

        self.gui.window.mainloop()

    def create_socket(self):
        try:
            self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            print('Server is offline')
            exit()

    def join_to_chat(self):
        self.user_name = self.gui.username_input_area.get()
        if not self.user_name.strip():
            self.gui.messagebox_error()
        else:
            self.gui.clear_text_input()
            self.gui.destroy_user_input()
            self.client_socket.send(self.user_name.encode('utf-8'))

    def send_to_server(self, event):
        if not self.user_name:
            self.gui.messagebox_error()
        else:
            self.msg = self.gui.grab_message()
            if self.msg:
                self.gui.clear_text_input()
                self.gui.handler_text_area(data=self.msg)
                self.client_socket.sendall(self.msg.encode('utf-8'))

    def listen_server(self):
        while not self.stop:
            try:
                self.msg = self.client_socket.recv(1024)
                self.gui.handler_text_area(data=self.msg)
            except ConnectionAbortedError as e:
                print(e, type(e))
            except ConnectionResetError:
                self.gui.offline_server()
                self.gui.window.destroy()
                self.client_socket.close()
                exit()

    def exit_from_chat(self):
        if self.gui.messagebox_exit():
            self.stop = True
            self.gui.window.destroy()
            self.client_socket.close()
            exit()


if __name__ == '__main__':
    client = Client('127.0.0.1', 6666)
    client.run()
