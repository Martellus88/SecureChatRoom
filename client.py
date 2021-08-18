import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import messagebox


class Client:

    def __init__(self, ip: str, port: int):

        self.ip = ip
        self.port = port

        self.window = None
        self.text_area = None
        self.text_input = None

        self.stop = False

        msg = tk.Tk()
        msg.withdraw()

        self.user_name = simpledialog.askstring('Имя пользователя', 'Введите имя ')

    def exit_from_chat(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop = True
            self.window.destroy()

            print(self.listen_thread)
            self.listen_thread.join()
            print(self.listen_thread)

            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            exit(0)

    def run(self):
        self.create_socket()
        self.init_window()
        self.init_text_area()
        self.init_input_area()

        self.listen_thread = threading.Thread(target=self.listen_server, daemon=True)  # TODO ?!
        self.listen_thread.start()

        # self.window.mainloop()

    def init_window(self):
        self.window = tk.Tk()
        self.window.configure(bg='gray88')
        self.window.geometry('800x600')
        self.window.resizable(width=False, height=False)

        self.window.protocol("WM_DELETE_WINDOW", self.exit_from_chat)

    def create_socket(self):
        try:
            self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client_socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            print('Server is offline')
            exit(0)

    def init_text_area(self):
        chat_label = tk.Label(self.window, text='Chat box:', bg='gray88')
        chat_label.config(font=('Roboto', 15))
        chat_label.pack(pady=3)

        self.text_area = scrolledtext.ScrolledText(master=self.window, width=90, background='white smoke',
                                                   font=("Roboto", 11))
        self.text_area.pack(side='top', padx=20, pady=5)
        self.text_area.config(state='disabled')

    def init_input_area(self):
        label_input = tk.Label(master=self.window, text='Enter your message: ', bg='gray88')
        label_input.config(font=('Roboto', 15))
        label_input.pack(pady=5)

        self.text_input = tk.Text(master=self.window, width=80, height=10, background='white smoke',
                                  font=("Roboto", 10))
        self.text_input.pack(side='bottom', padx=10, pady=13)
        self.text_input.focus_set()

        self.text_input.bind('<Return>', func=self.send_to_server)
        self.text_input.bind('<Shift-Return>', func=lambda event: self.text_input.insert(tk.END, ''))

    def send_to_server(self, event):
        msg = self.text_input.get('1.0', tk.END).strip()

        if msg:
            self.text_input.delete('0.0', tk.END)
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, 'Вы: ' + msg + '\n')
            self.text_area.yview(tk.END)
            self.client_socket.sendall(msg.encode('utf-8'))
            self.text_area.config(state='disabled')

    def listen_server(self):
        while not self.stop:
            try:
                serv_msg = self.client_socket.recv(1024)

                if serv_msg.decode('utf-8') == 'username':
                    self.client_socket.sendall(self.user_name.encode('utf-8'))
                else:
                    self.text_area.config(state='normal')
                    self.text_area.insert(tk.END, serv_msg.decode('utf-8'))
                    self.text_area.yview(tk.END)
                    self.text_area.config(state='disabled')
            # except ConnectionRefusedError as e:
            #     print(type(e))
            except ConnectionResetError:
                print('Server is offline')


if __name__ == '__main__':
    client = Client('127.0.0.1', 6666)
    client.run()
    client.window.mainloop()
