import socket

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('localhost',4000))
server.listen()
conn, addr = server.accept()
while True:

    print('Подключено: ',addr)
    data = server.recv(1024)
    if not data:
        break
    conn.send(data.upper())
    print(data.upper())
    conn.close()



a = 123
def i():
