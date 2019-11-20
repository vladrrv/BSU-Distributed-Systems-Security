import socket
import os
import logging
import time
from threading import Thread, Event
from Crypto.PublicKey import RSA
from Crypto import Random
from CryptoPlus.Cipher import python_Serpent as serpent

from flask import Flask, render_template, request, session, redirect

from utils import *

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app_host = '127.0.0.1'
app_port = 5000
app = Flask(__name__)
app.secret_key = os.urandom(12)
thread = Thread(target=app.run, kwargs=dict(debug=False, host=app_host, port=app_port))
login_event = Event()
code_event = Event()
expired_event = Event()


def generate_new_key(l=1024, save=True):
    # Generate private and public keys
    random_generator = Random.new().read
    private_key = RSA.generate(l, random_generator)
    if save:
        set_reg('private_key', private_key.exportKey().decode())
    return private_key


def run_client():
    cipher = None
    decipher = None

    def send_msg(msg, to_cipher=True):
        if type(msg) is str:
            msg = msg.encode(ENC)
        encr_msg = cipher.encrypt(msg) if to_cipher and cipher is not None else msg
        server.send(encr_msg)

    def recv_msg(to_decipher=True, decode=False):
        encr_msg = server.recv(4096)
        msg = decipher.decrypt(encr_msg) if to_decipher and decipher is not None else encr_msg
        return msg.decode() if decode else msg

    def get_session_key():
        reg_private_key = get_reg('private_key')
        if reg_private_key is None:
            private_key = generate_new_key()
        else:
            private_key = RSA.importKey(reg_private_key.encode(ENC))
        public_key = private_key.publickey()

        # Send public key to server
        send_msg(public_key.exportKey(), to_cipher=False)
        print("Sent public key to server.")
        sess_key = private_key.decrypt(recv_msg())
        print("Received session key from server.")
        print(f"Please log in here: http://{app_host}:{app_port}/")
        # print(sess_key)
        return sess_key

    def get_command():
        cmd, *args = input("\nEnter command: ").split()
        return cmd, args

    def auth(username, password):

        send_msg(username)
        send_msg(password)

        auth_result = recv_msg(decode=True)
        if auth_result == MSG.SUCCESS:
            return True
        else:
            print("Authentication failed:", auth_result)
        return False

    def code_check(code):
        send_msg(code)
        result = recv_msg(decode=True)
        if result == MSG.SUCCESS:
            return True
        else:
            print("Code check failed:", result)
        return False

    @app.route('/')
    def home():
        if expired_event.is_set():
            session['logged_in'] = False
            session['confirmed'] = False
            expired_event.clear()
        if not session.get('logged_in'):
            return render_template('login.html', wrong=session.get('wrong', False))
        elif not session.get('confirmed'):
            return render_template('code.html', wrong=session.get('wrong', False))
        else:
            return "Hello!"

    @app.route('/login', methods=['POST'])
    def login():
        if auth(request.form['username'], request.form['password']):
            session['wrong'] = False
            session['logged_in'] = True
            login_event.set()
        else:
            session['wrong'] = True
        return redirect('/')

    @app.route('/code', methods=['POST'])
    def confirm():
        if code_check(request.form['code']):
            session['wrong'] = False
            session['confirmed'] = True
            code_event.set()
        else:
            session['wrong'] = True
        return redirect('/')

    def run_session(sess_key):
        nonlocal cipher, decipher
        cipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
        decipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)

        while not login_event.is_set():
            time.sleep(1)

        while not code_event.is_set():
            time.sleep(1)

        login_event.clear()
        code_event.clear()

        while True:
            command, args = get_command()
            if command == 'r':
                if len(args) == 0:
                    print("You need to specify file name.")
                    continue
                filename = args[0]
                send_msg(CMD.RECV)
                send_msg(filename)
                print("Sent filename to server.")
                result = recv_msg(decode=True)
                if result == MSG.SUCCESS:
                    text = recv_msg(True)
                    print("Received text from server.")
                    print(text)
                elif result == MSG.ERROR:
                    error_text = recv_msg(decode=True)
                    print("Failed to receive text from server:", error_text)
                elif result == MSG.EXP_SESS:
                    print("Session expired.")
                    expired_event.set()
                    return True
                else:
                    print("Invalid result.")

            elif command == 'q':
                send_msg(CMD.QUIT)
                print("Quit.")
                return False

            elif command == 's':
                if len(args) == 0:
                    print("You need to specify file name.")
                    continue
                filename = args[0]
                text = read_file(filename)
                short_name = filename.split(sep='/')[-1]
                text = '\0'.join([short_name, text])
                send_msg(CMD.SEND)
                send_msg(text)
                print("Sent text to server.")
                result = recv_msg(decode=True)
                if result == MSG.EXP_SESS:
                    print("Session expired.")
                    expired_event.set()
                    return True

            elif command == 'g':
                private_key = generate_new_key()
                print("Generated new private RSA key.")

            else:
                print("Unknown command.")

    server = socket.socket()
    host = "localhost"
    port = 7777
    server.connect((host, port))
    print("Connected to server.")
    thread.start()

    while run_session(get_session_key()):
        cipher = None
        decipher = None
    print("Client stopped.")
    server.close()


if __name__ == "__main__":
    run_client()
