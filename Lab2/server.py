import socket
from Crypto.PublicKey import RSA
from CryptoPlus.Cipher import python_Serpent as serpent
import random
import os
import base64
import time

from utils import *

USERS_PATH = '.\\users'
SESSION_MAX_TIME = 90


def authenticate(user, password):
    user_str = user.decode()
    password_str = base64.b64encode(password).decode()
    up = f"{user_str}_{password_str}"
    user_dir = os.path.join(USERS_PATH, up)
    return os.path.isdir(user_dir), user_dir




def run_server():
    mysocket = socket.socket()
    host = socket.gethostbyname('localhost')
    port = 7777
    print("host = " + host)

    # Prevent socket.error: [Errno 98] Address already in use
    mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mysocket.bind((host, port))
    mysocket.listen(5)
    c, addr = mysocket.accept()

    def send_msg(msg, cipher=None):
        if type(msg) is str:
            msg = msg.encode(ENC)
        encr_msg = cipher.encrypt(msg) if cipher is not None else msg
        c.send(encr_msg)

    def recv_msg(decipher=None, decode=False):
        encr_msg = c.recv(4096)
        msg = decipher.decrypt(encr_msg) if decipher is not None else encr_msg
        return msg.decode() if decode else msg

    def generate_session_key():
        sess_key = bytes(random.getrandbits(8) for _ in range(16))
        print("Generated session key:", sess_key)

        # Receive public key from client
        client_string = c.recv(1024)
        client_public_key = RSA.importKey(client_string)
        print("Public key received from client.")

        send_msg(client_public_key.encrypt(sess_key, 32)[0])
        print("Sent session key to client.")
        return sess_key

    def run_session(sess_key):
        cipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
        decipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)

        while True:
            login = recv_msg(decipher)
            password = recv_msg(decipher)
            is_auth, user_dir = authenticate(login, password)
            if is_auth:
                send_msg(MSG.SUCCESS, cipher)
                break
            else:
                send_msg("invalid username/password", cipher)

        t1 = time.clock()
        while True:
            cmd = recv_msg(decipher, True)
            if cmd == CMD.RECV:
                t2 = time.clock()
                if t2-t1 > SESSION_MAX_TIME:
                    print("Session expired.")
                    c.recv(4096)
                    send_msg(MSG.EXP_SESS, cipher)
                    return True
                filename = recv_msg(decipher, True)
                print("Received filename from client.")
                print(filename)
                path = os.path.join(user_dir, filename)
                text = read_file(path)
                if text is None:
                    send_msg(MSG.ERROR, cipher)
                    text = "No such file!"
                else:
                    send_msg(MSG.SUCCESS, cipher)
                send_msg(text, cipher)
                print("Sent text to client.")
            elif cmd == CMD.SEND:
                t2 = time.clock()
                if t2-t1 > SESSION_MAX_TIME:
                    print("Session expired.")
                    c.recv(4096)
                    c.recv(4096)
                    send_msg(MSG.EXP_SESS, cipher)
                    return True
                text = recv_msg(decipher, True)
                print("Received text from client.")
                print(text)
                filename = recv_msg(decipher, True)
                print("Received filename from client.")
                print(filename)
                path = os.path.join(user_dir, filename)
                save_file(text, path)
                send_msg(MSG.SUCCESS, cipher)

            elif cmd == CMD.QUIT:
                return False
            else:
                print("Invalid cmd.")

    while run_session(generate_session_key()):
        pass

    print("Server stopped.")
    c.close()


if __name__ == "__main__":
    run_server()

