import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox


class Gui:

    def __init__(self, client_cls):
        self.client = client_cls

        self.text_area = None
        self.text_input = None
        self.username_input_area = None
        self.frame_username_input = None
        self.frame_text_input = None

        self.window = tk.Tk()

    def init_gui(self):
        self.init_window()
        self.init_text_area()
        self.init_username_input()
        self.init_input_area()

    def init_window(self):
        self.window.title('Stay Safe Exile...')
        self.window.configure(bg='gray88')
        self.window.geometry('800x600')
        self.window.resizable(width=False, height=False)

        self.window.protocol("WM_DELETE_WINDOW", self.client.exit_from_chat)

    def init_text_area(self):
        frame_text_area = tk.Frame(bg='gray88')

        chat_label = tk.Label(master=frame_text_area, text='Chat box:', bg='gray88')
        chat_label.config(font=('Roboto', 15))
        chat_label.pack(side='top', anchor='w', padx=10)

        self.text_area = scrolledtext.ScrolledText(master=frame_text_area, width=90, background='white smoke',
                                                   font=("Roboto", 11))
        self.text_area.pack(side='left', padx=10)
        self.text_area.config(state='disabled')

        frame_text_area.pack(side='top')

    def init_username_input(self):
        self.frame_username_input = tk.Frame(bg='gray88')

        chat_label = tk.Label(master=self.frame_username_input, text='username:', bg='gray88')
        chat_label.config(font=('Roboto', 12))
        chat_label.pack(side='left', padx=15)

        self.username_input_area = tk.Entry(master=self.frame_username_input, width=20, background='white smoke',
                                            font=("Roboto", 11))
        self.username_input_area.pack(side='left', anchor='nw', pady=10)

        join_button = tk.Button(self.frame_username_input, text="join", width=5, command=self.client.join_to_chat,
                                bd=3)
        join_button.pack(side='left', padx=10)

        self.username_input_area.focus_set()

        self.frame_username_input.pack(side='top', anchor='n')

    def init_input_area(self):
        self.frame_text_input = tk.Frame(bg='gray88')

        label_input = tk.Label(master=self.frame_text_input, text='Enter your message: ', bg='gray88')
        label_input.config(font=('Roboto', 14))
        label_input.pack(side='top', anchor='w')

        self.text_input = tk.Text(master=self.frame_text_input, width=80, height=5, background='white smoke',
                                  font=("Roboto", 10))
        self.text_input.pack(side='left', pady=10)

        self.text_input.bind('<Return>', func=self.client.send_to_server)
        self.text_input.bind('<Shift-Return>', func=lambda event: self.text_input.insert(tk.END, ''))

        self.frame_text_input.pack(side='top')

    def handler_text_area(self, data):
        letter = data.decode() if isinstance(data, bytes) else 'You: ' + self.client.msg + '\n'

        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, letter)
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')

    def grab_message(self):
        return self.text_input.get('1.0', tk.END).strip()

    def destroy_user_input(self):
        self.frame_username_input.destroy()
        self.frame_text_input.pack(side='top', pady=20)
        self.text_input.focus_set()

    def messagebox_error(self):
        messagebox.showerror('Enter nickname', 'Please enter a nickname')
        self.username_input_area.delete(0, tk.END)
        return

    def messagebox_exit(self):
        return messagebox.askokcancel("Exit", "Do you want to exit the program?")

    def clear_text_input(self):
        self.text_input.delete('1.0', tk.END)

    def offline_server(self):
        messagebox.showinfo('Server is offline', 'Server is offline')
