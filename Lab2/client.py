import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from CryptoPlus.Cipher import python_Serpent as serpent

# Generate private and public keys
random_generator = Random.new().read
private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()

server = socket.socket()
host = "localhost"
port = 7777

server.connect((host, port))

# Send public key string to server
server.send(public_key.exportKey())
print("Sent public key to server.")

ciphertext = server.recv(1024)
print("Received encrypted text from server.")

server_string = server.recv(1024)
print("Received encrypted session key from server.")
encrypted_sess_key = server_string
sess_key = private_key.decrypt(encrypted_sess_key)
print('Session key: ', sess_key)


# IV = b'0000000000000000'
decipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
text = decipher.decrypt(ciphertext).decode()
print(text)

# Tell server to finish connection
# server.sendall(b"Quit")
print(server.recv(1024).decode())
server.close()
