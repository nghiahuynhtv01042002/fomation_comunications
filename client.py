import socket
import time
import threading
class odomerty_follower:
    def __init__(self, cmd, x, y, theta):
        self.cmd_f = cmd
        self.x_f = x
        self.y_f = y
        self.theta_f = theta
    

def decoder_frame_data(data_received):
    split_index_CMD_start = data_received.index(':')
    split_index_CMD_stop = data_received.index('#',split_index_CMD_start + 1)

    split_index_X_start = data_received.index(':',split_index_CMD_stop+1)
    split_index_X_stop = data_received.index('#',split_index_X_start+1)

    split_index_Y_start = data_received.index(':',split_index_X_stop+1)
    split_index_Y_stop = data_received.index('#',split_index_Y_start+1)

    split_index_Theta_start = data_received.index(':',split_index_Y_stop+1)
    split_index_Theta_stop = data_received.index('#',split_index_Theta_start+1)

    cmd = data_received[split_index_CMD_start+1:split_index_CMD_stop]
    X = float(data_received[split_index_X_start+1:split_index_X_stop])
    Y = float(data_received[split_index_Y_start+1:split_index_Y_stop])
    Theta = float(data_received[split_index_Theta_start+1:split_index_Theta_stop])   
    return cmd, X, Y, Theta
# create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client_socket.connect(('localhost', 12345))
myclient = odomerty_follower("stp",0.00,0.00,0.00)
data_fag = 1
# odom_string_f = "!cmd_f:{}#x_f{:.2f}:y_f:{:.2f}#theta_f:{:.2f}#\n".format(myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f)
# print(odom_string_f)
def recieve_data_from_server():
    global client_socket
    global myclient
    global data_fag
    count = 0
    while True:
        # # enter message
        # message = "I Am TXN\n"
        # # send data to server
        # client_socket.send(message.encode())
        
        # # receive data from server
        # data = client_socket.recv(1024).decode()
        # # print(f"Received from server: {data} {count}")
        # print("Received from server: {} {}".format(data, count))
        # count += 1
        # time.sleep(2)

        # # enter message
        # message = "I Am TXN\n"
        # # send data to server
        # client_socket.send(message.encode())
        
        # receive data from server
        data = client_socket.recv(1024).decode()
        if not data: 
            print("can not recieve data from server\n")
            data_fag = 0
            break
        # print("Received from server: {} {}".format(data, count))

        myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f = decoder_frame_data(data)
        odom_string_f = "cmd_f: {}\nx_f: {:.2f}\ny_f: {:.2f}\ntheta_f: {:.2f}".format(myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f)
        print(odom_string_f)
        count += 1
        #calculate PI here 

        time.sleep(2)

def send_data_to_MCU():
    it = 0
    while True:
       
        print("PI output{}\n".format(it))
        it+=1
        if data_fag == 0:
            break
        time.sleep(2)

def main():
    global myclient
    global client_socket
    thread1_recive_odom = threading.Thread(target=recieve_data_from_server)
    thread2_send_data_to_MCU = threading.Thread(target= send_data_to_MCU)
    thread1_recive_odom.start()
    thread2_send_data_to_MCU.start()
    # Let the main thread wait until the thread1_recive_odom finishes its job
    thread1_recive_odom.join()
    thread2_send_data_to_MCU.join()
    # close connection
    client_socket.close()
    
if __name__ == "__main__":
    main()
