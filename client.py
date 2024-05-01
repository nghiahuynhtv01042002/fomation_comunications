import socket
import time
import threading

# create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client_socket.connect(('localhost', 12345))

def recieve_data_from_server():
    global client_socket
    count = 0
    while True:
        # enter message
        message = "I Am TXN\n"
        # send data to server
        client_socket.send(message.encode())
        
        # receive data from server
        data = client_socket.recv(1024).decode()
        # print(f"Received from server: {data} {count}")
        print("Received from server: {} {}".format(data, count))
        count += 1
        time.sleep(2)

def main():
    global client_socket
    thread1_recive_odom = threading.Thread(target=recieve_data_from_server)
    thread1_recive_odom.start()
    # Let the main thread wait until the thread1_recive_odom finishes its job
    thread1_recive_odom.join()
    # close connection
    client_socket.close()

if __name__ == "__main__":
    main()
