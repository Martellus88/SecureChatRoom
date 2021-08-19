import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox


class Client:

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.text_area = None
        self.text_input = None
        self.user_area = None

        self.stop = False

        self.window = tk.Tk()
        self.window.withdraw()

    def exit_from_chat(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the program?"):
            self.stop = True
            self.window.destroy()
            self.client_socket.close()
            exit(0)

    def run(self):
        self.create_socket()
        self.init_window()
        self.init_text_area()
        self.init_username_input()
        self.init_input_area()

        listen_thread = threading.Thread(target=self.listen_server)
        listen_thread.start()

        self.window.mainloop()

    def init_window(self):
        self.window.deiconify()
        self.window.title('Stay Safe Exile...')
        self.window.configure(bg='gray88')
        self.window.geometry('800x600')
        self.window.resizable(width=False, height=False)

        self.window.protocol("WM_DELETE_WINDOW", self.exit_from_chat)

    def create_socket(self):
        try:
            self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            print('Server is offline')
            exit(0)

    def init_text_area(self):
        frame = tk.Frame(bg='gray88')

        chat_label = tk.Label(frame, text='Chat box:', bg='gray88')
        chat_label.config(font=('Roboto', 15))
        chat_label.pack(side='top', anchor='w', padx=10)

        self.text_area = scrolledtext.ScrolledText(master=frame, width=90, background='white smoke',
                                                   font=("Roboto", 11))
        self.text_area.pack(side='left', padx=10)
        self.text_area.config(state='disabled')

        frame.pack(side='top')

    def init_input_area(self):
        frame = tk.Frame(bg='gray88')

        label_input = tk.Label(master=frame, text='Enter your message: ', bg='gray88')
        label_input.config(font=('Roboto', 14))
        label_input.pack(side='top', anchor='w')

        self.text_input = tk.Text(master=frame, width=80, height=5, background='white smoke',
                                  font=("Roboto", 10))
        self.text_input.pack(side='left', pady=10)

        self.text_input.bind('<Return>', func=self.send_to_server)
        self.text_input.bind('<Shift-Return>', func=lambda event: self.text_input.insert(tk.END, ''))

        frame.pack(side='top')

    def init_username_input(self):
        frame = tk.Frame(bg='gray88')

        chat_label = tk.Label(frame, text='username:', bg='gray88')
        chat_label.config(font=('Roboto', 12))
        chat_label.pack(side='left', padx=15)

        self.user_area = tk.Entry(master=frame, width=20, background='white smoke',
                                  font=("Roboto", 11))
        self.user_area.pack(side='left', anchor='nw', pady=10)

        join_button = tk.Button(frame, text="join", width=5, command=self.join_to_server, bd=3)
        join_button.pack(side='left', padx=10)

        self.user_area.focus_set()

        frame.pack(side='top', anchor='n')

    def join_to_server(self):
        if len(self.user_area.get()) == 0:
            messagebox.showerror('Enter nickname', 'Please enter a nickname')
            return
        self.user_area.config(state='disable')
        self.user_name = self.user_area.get()
        self.client_socket.send(self.user_name.encode('utf-8'))

    def send_to_server(self, event):
        if len(self.user_area.get()) == 0:
            messagebox.showerror('Enter nickname', 'Please enter a nickname')
            return

        msg = self.text_input.get('1.0', tk.END).strip()

        if msg:
            self.text_input.delete('0.0', tk.END)
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, 'You: ' + msg + '\n')
            self.text_area.yview(tk.END)
            self.client_socket.sendall(msg.encode('utf-8'))
            self.text_area.config(state='disabled')

    def listen_server(self):
        while not self.stop:
            try:
                serv_msg = self.client_socket.recv(1024)

                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, serv_msg.decode('utf-8'))
                self.text_area.yview(tk.END)
                self.text_area.config(state='disabled')

            except ConnectionAbortedError as e:
                print(e, type(e))
            except ConnectionResetError:
                print('Server is offline')


if __name__ == '__main__':
    client = Client('127.0.0.1', 6666)
    client.run()
