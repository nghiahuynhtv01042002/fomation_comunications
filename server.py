import socket
import time

count = 0


class odometry_server:
    def __init__(self, cmd, x, y, theta):
        self.cmd = cmd
        self.x = x
        self.y = y
        self.theta = theta
    def update(self):
        self.x += 0.05
        self.y += 0.05 
        self.theta += 0

# Sử dụng
myServer = odometry_server("stp",0.0, 0.0, 0.0)
odom_string = "!cmd:{}#x{}:y:{}#theta:{}#\n".format(myServer.cmd,myServer.x,myServer.y,myServer.theta)
print(odom_string)
#create socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# listen conect to port 12345
# server_socket.bind(('127.0.0.1', 12345))
server_socket.bind(('localhost', 12345))
# server_socket.bind(('192.168.31.252', 12345))


# server_socket.bind(('192.168.207.70', 12345))
server_socket.listen(5)

print("Server is listening...")

# accept conection from client
client_socket, addr = server_socket.accept()

# print(f"Connection from {addr} has been established.")
print("Connection from {} has been established.".format(addr))
# making handle client here
while True:
    
    # # recieve data from client
    data = client_socket.recv(1024).decode().strip()
    if not data:
        break
    # print(f"Received from client: {data} {count}")
    print("Received from client: {}{}".format(data,count))
    # count +=1
 
    # send back data to client
    # data_send = "ack " + data
    # client_socket.send(data_send.encode())

    odom_string = "!cmd:{}#x{:.2f}:y:{:.2f}#theta:{:.2f}#\n".format(myServer.cmd,myServer.x,myServer.y,myServer.theta)
    client_socket.send(odom_string.encode())
    # print(odom_string)
    myServer.update()
    count +=1
    time.sleep(2)

# close conect
client_socket.close()
server_socket.close()
