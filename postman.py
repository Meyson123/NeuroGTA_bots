import socket

sock = socket.socket()
sock.connect(('localhost', 4000))
print('Подключено')
sock.send(b"13:'123")

data = sock.recv(1024)
sock.close()

print(data)
