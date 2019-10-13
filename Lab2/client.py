import socket
from Crypto.PublicKey import RSA

server = socket.socket()
host = "localhost"
port = 7777

server.connect((host, port))

#Tell server that connection is OK
server.sendall(b"Client: OK")

#Receive public key string from server
server_string = server.recv(1024)

#Remove extra characters
server_string = server_string.replace(b"public_key=", b'')
server_string = server_string.replace(b"\r\n", b'')

#Convert string to key
server_public_key = RSA.importKey(server_string)

#Encrypt message and send to server
message = b'This is my secret message.'
encrypted = server_public_key.encrypt(message, 32)[0]
server.sendall(b'encrypted_message='+encrypted)

#Server's response
server_response = server.recv(1024)
server_response = server_response.replace(b"\r\n", b'')
if server_response == b"Server: OK":
    print("Server decrypted message successfully")

#Tell server to finish connection
server.sendall(b"Quit")
print(server.recv(1024).decode()) #Quit server response
server.close()
