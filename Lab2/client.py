import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from CryptoPlus.Cipher import python_Serpent as serpent

from utils import *


def generate_new_key(l=1024, save=True):
    # Generate private and public keys
    random_generator = Random.new().read
    private_key = RSA.generate(l, random_generator)
    if save:
        set_reg('private_key', private_key.exportKey().decode())
    return private_key


def run_client():
    server = socket.socket()
    host = "localhost"
    port = 7777
    server.connect((host, port))
    print("Connected to server.")

    def send_msg(msg, cipher=None):
        if type(msg) is str:
            msg = msg.encode(ENC)
        encr_msg = cipher.encrypt(msg) if cipher is not None else msg
        server.send(encr_msg)

    def recv_msg(decipher=None, decode=False):
        encr_msg = server.recv(4096)
        msg = decipher.decrypt(encr_msg) if decipher is not None else encr_msg
        return msg.decode() if decode else msg

    def get_session_key():
        reg_private_key = get_reg('private_key')
        if reg_private_key is None:
            private_key = generate_new_key()
        else:
            private_key = RSA.importKey(reg_private_key.encode(ENC))
        public_key = private_key.publickey()

        # Send public key to server
        send_msg(public_key.exportKey())
        print("Sent public key to server.")
        sess_key = private_key.decrypt(recv_msg())
        print("Received session key from server.")
        return sess_key

    def run_session(sess_key):
        cipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
        decipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)

        while True:
            login = input("\nLogin: ")
            password = input("Password: ")

            send_msg(login, cipher)
            send_msg(password, cipher)

            auth_result = recv_msg(decipher, True)
            if auth_result == MSG.SUCCESS:
                break
            else:
                print("Authentication failed:", auth_result)

        def get_command():
            cmd, *args = input("\nEnter command: ").split()
            return cmd, args

        while True:
            command, args = get_command()
            if command == 'r':
                if len(args) == 0:
                    print("You need to specify file name.")
                    continue
                filename = args[0]
                send_msg(CMD.RECV, cipher)
                send_msg(filename, cipher)
                print("Sent filename to server.")
                result = recv_msg(decipher, True)
                if result == MSG.SUCCESS:
                    text = recv_msg(decipher, True)
                    print("Received text from server.")
                    print(text)
                elif result == MSG.ERROR:
                    error_text = recv_msg(decipher, True)
                    print("Failed to receive text from server:", error_text)
                elif result == MSG.EXP_SESS:
                    print("Session expired.")
                    return True
                else:
                    print("Invalid result.")

            elif command == 'q':
                send_msg(CMD.QUIT, cipher)
                print("Quit.")
                return False

            elif command == 's':
                if len(args) == 0:
                    print("You need to specify file name.")
                    continue
                filename = args[0]
                text = read_file(filename)
                send_msg(CMD.SEND, cipher)
                send_msg(text, cipher)
                print("Sent text to server.")
                send_msg(filename.split(sep='/')[-1], cipher)
                print("Sent filename to server.")
                result = recv_msg(decipher, True)
                if result == MSG.EXP_SESS:
                    print("Session expired.")
                    return True

            elif command == 'g':
                private_key = generate_new_key()
                print("Generated new private RSA key.")

            else:
                print("Unknown command.")

    while run_session(get_session_key()):
        pass

    print("Client stopped.")
    server.close()


if __name__ == "__main__":
    run_client()
