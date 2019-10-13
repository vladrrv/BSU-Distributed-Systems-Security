import socket
from Crypto.PublicKey import RSA
from Crypto import Random

#Generate private and public keys
random_generator = Random.new().read
private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()

#Declartion
mysocket = socket.socket()
host = socket.gethostbyname('localhost')
port = 7777
encrypt_str = b'encrypted_message='

if host == "127.0.1.1":
    import commands
    host = commands.getoutput("hostname -I")
print("host = " + host)

#Prevent socket.error: [Errno 98] Address already in use
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

mysocket.bind((host, port))

mysocket.listen(5)

c, addr = mysocket.accept()

while True:

    #Wait until data is received.
    data = c.recv(1024)
    data = data.replace(b"\r\n", b'') #remove new line character

    if data == b"Client: OK":
        c.send(b"public_key=" + public_key.exportKey() + b"\n")
        print("Public key sent to client.")

    elif encrypt_str in data: #Reveive encrypted message and decrypt it.
        data = data.replace(encrypt_str, b'')
        print("Received:\nEncrypted message = "+str(data))
        encrypted = eval(str(data))
        decrypted = private_key.decrypt(encrypted)
        c.send(b"Server: OK")
        print("Decrypted message = " + decrypted.decode())

    elif data == b"Quit": break

#Server to stop
c.send(b"Server stopped\n")
print("Server stopped")
c.close()