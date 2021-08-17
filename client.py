import socket
import threading
import tkinter as tk


ip = '127.0.0.1'
port = 6666

client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
client_socket.connect((ip, port))

window = tk.Tk()

text_area = tk.Text(master=window, width=50)
text_area.grid(row=0, column=0, padx=15, pady=15)

text_input = tk.Entry(master=window, width = 50)
text_input.grid(row=1, column=0, padx=15, pady=15)

def send_to_server():
    msg = text_input.get()
    text_area.insert(tk.END,  '\nВы:  ' + msg)
    client_socket.sendall(msg.encode('utf-8'))

btn_send = tk.Button(master=window, text='Отправить', width=15, command=send_to_server)
btn_send.grid(row=2, column=0, padx=10, pady=10)

def listen():
    while True:
        serv_msg = client_socket.recv(1024)
        text_area.insert(tk.END, '\n'+ serv_msg.decode('utf-8'))

listen_thread = threading.Thread(target=listen)



if __name__ == '__main__':
    listen_thread.start()
    window.mainloop()