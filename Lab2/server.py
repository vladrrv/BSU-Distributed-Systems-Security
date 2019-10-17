import socket
from Crypto.PublicKey import RSA
from CryptoPlus.Cipher import python_Serpent as serpent


plaintext = "He could not see the ground. It was lost in the ever increasing complexities of man-made structures. He " \
            "could see no horizon other than that of metal against sky, stretching out to almost uniform grayness, " \
            "and he knew it was so over all the land-surface of the planet. There was scarcely any motion to be seen " \
            "- a few pleasure-craft lazed against the sky-but all the busy traffic of billions of men were going on, " \
            "he knew, beneath the metal skin of the world. ".encode('UTF-8')

# Declartion
mysocket = socket.socket()
host = socket.gethostbyname('localhost')
port = 7777

if host == "127.0.1.1":
    import commands
    host = commands.getoutput("hostname -I")
print("host = " + host)

# Prevent socket.error: [Errno 98] Address already in use
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

mysocket.bind((host, port))

mysocket.listen(5)

c, addr = mysocket.accept()

# Receive public key from client
client_string = c.recv(1024)
client_public_key = RSA.importKey(client_string)
print("Public key received from client.")

sess_key = b'1234567890abcdef'
# IV = b'0000000000000000'
print("Generated session key:", sess_key)

cipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
ciphertext = cipher.encrypt(plaintext)
#decipher = serpent.new(key=sess_key, mode=serpent.MODE_CFB, segment_size=16)
#text = decipher.decrypt(ciphertext)
#print(text)

c.send(ciphertext)
c.send(client_public_key.encrypt(sess_key, 32)[0])

# Wait until data is received.
# data = c.recv(1024)
# if data == b"Quit": break

# Server to stop
c.send(b"Server stopped\n")
print("Server stopped")
c.close()
