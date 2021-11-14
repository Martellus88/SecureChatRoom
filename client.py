import socket
import threading
from hashlib import sha256

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP
from client_gui import Gui


class Client:

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

        self.stop = False

        self.__public_key = None
        self.__ssk = None

        self.user_name = None
        self.client_socket = None
        self.msg = ''

        self.gui = Gui(self)

    def run(self):
        self.create_socket()
        self.gui.init_gui()

        self.gui.window.mainloop()

    def create_socket(self):
        try:
            self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            self.gui.messagebox_info('Offline', 'Server if offline')
            exit()

    def __handshake(self):
        self.generate_rsa_keys()
        self.client_socket.sendall(self.__public_key)
        key_from_server = self.client_socket.recv(2048)
        self.decrypt_session_key(key_from_server)

    def join_to_chat(self):
        self.user_name = self.gui.username_input_area.get()
        if not self.user_name.strip():
            self.gui.messagebox_error()
        else:
            self.gui.clear_text_input()
            self.gui.destroy_user_input()
            self.client_socket.sendall(self.user_name.encode('utf-8'))

            self.__handshake()

            listen_thread = threading.Thread(target=self.listen_server, daemon=True)
            listen_thread.start()

    def send_to_server(self, event):
        if not self.user_name:
            self.gui.messagebox_error()
        else:
            self.msg = self.gui.grab_message()
            if self.msg:
                self.gui.clear_text_input()
                self.gui.handler_text_area(data=self.msg)
                nonce, tag, cipher_text = self.encrypt_message(message=self.msg.encode('utf-8'))
                self.client_socket.sendall(nonce + b'!:@' + tag + b'!:@' + cipher_text)

    def listen_server(self):
        while not self.stop:
            try:
                self.msg = self.client_socket.recv(2048)
                if b'Connection' in self.msg:
                    self.gui.handler_text_area(data=self.msg)
                elif b'LEFT' in self.msg:
                    self.gui.handler_text_area(data=self.msg.replace(b'&??*', b' '))
                else:
                    nickname, letter = self.msg.split(b'&??*')
                    received_letter = self.decrypt_message(letter)
                    self.gui.handler_text_area(data=nickname + b': ' + received_letter + b'\n')
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(e, type(e))
                self.emergency_closure(title='Offline', text='Server is offline')

    def exit_from_chat(self):
        if self.gui.messagebox_exit():
            self.stop = True
            self.gui.window.destroy()
            self.client_socket.close()
            exit()

    def emergency_closure(self, title, text):
        self.gui.messagebox_info(title=title, text=text)
        self.gui.window.destroy()
        self.client_socket.close()
        exit()

    def generate_rsa_keys(self):
        key = RSA.generate(2048)

        private_key = key.export_key()
        with open('private_key.pem', 'wb') as f:
            f.write(private_key)
        self.__public_key = key.public_key().export_key()

    def encrypt_message(self, message):
        try:
            cipher_aes = AES.new(self.__ssk, AES.MODE_EAX)
            cipher_text, tag = cipher_aes.encrypt_and_digest(message)
            return cipher_aes.nonce, tag, cipher_text
        except ValueError as e:
            print('Hacking attempt!', e)
            self.emergency_closure(title='Hacking attempt!', text='Hacking attempt!!! Termination of work')

    def decrypt_message(self, message):
        try:
            text = message.split(b'!:@')
            nonce, tag, cipher_text = text
            cipher_aes = AES.new(self.__ssk, AES.MODE_EAX, nonce)
            data = cipher_aes.decrypt_and_verify(cipher_text, tag)
            return data
        except ValueError as e:
            print('Hacking attempt!', e)
            self.emergency_closure(title='Hacking attempt!', text='Hacking attempt!!! Termination of work')

    def decrypt_session_key(self, crypto_session_key):
        try:
            ssk, hash_ssk = crypto_session_key.split(b'&-^*')

            private_key = RSA.import_key(open('private_key.pem').read())
            cipher_rsa = PKCS1_OAEP.new(private_key)
            self.__ssk = cipher_rsa.decrypt(ssk)

            check_hash_ssk = sha256(self.__ssk).digest()
            if hash_ssk != check_hash_ssk:
                raise ValueError

        except ValueError as e:
            print('Hacking attempt!', e)
            self.emergency_closure(title='Hacking attempt!', text='Hacking attempt!!! Termination of work')


if __name__ == '__main__':
    client = Client('127.0.0.1', 6666)
    client.run()
