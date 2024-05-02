import socket
import time
import threading
import math
import serial

class PIController:
    def __init__(self, Kp, Ki):
        self.Kp = Kp
        self.Ki = Ki
        self.error = 0.0
        self.prev_error = 0.0
        self.integral = 0.0

    def pi_output(self,setpoint,current_value):
        error = setpoint - current_value
        self.integral += error 
        # derivative = (error - self.prev_error) / dt
        output = self.Kp * error + self.Ki * self.integral
        self.prev_error = error
        return output
    
class odomerty_follower:
    def __init__(self, cmd, x, y, theta, cmdf_atc,xf_atc, yf_atc,thetaf_atc):
        self.cmd_f_d = cmd
        self.x_f_d = x
        self.y_f_d = y
        self.theta_f_d = theta

        self.cmdf_atc = cmdf_atc 
        self.xf_atc = xf_atc
        self.yf_atc = yf_atc
        self.thetaf_atc = thetaf_atc
    

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

##init value 
# create socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client_socket.connect(('localhost', 12345))
#init odom follower
myclient = odomerty_follower("stp",0.00,0.00,0.00, "stp",0.00,0.00,0.00)
data_fag = 1
# odom_string_f = "!cmd_f:{}PI#x_f{:.2f}:y_f:{:.2f}#theta_f:{:.2f}#\n".format(myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f)
# print(odom_string_f)

#init PI controler
vx_PI = PIController(1.50,0.1)
vy_PI = PIController(1.50,0.1)

vx = 0.0
vy = 0.0

distance_follow_and_lead = 0.2
Radius_wheel = 0.065/2
L =0.18


def recieve_data_from_server():
    global client_socket
    global myclient
    global data_fag
    global distance_follow_and_lead,L,vx,vy
    global vx_PI
    global vy_PI
    count = 0
    while True:        
        # receive data from server
        data = client_socket.recv(1024).decode()
        if not data: 
            print("can not recieve data from server\n")
            data_fag = 0
            break
        # print("Received from server: {} {}".format(data, count))
        cmd_L,x_L,y_L,theta_l = decoder_frame_data(data)
        # calcutal desired positon of follower
        myclient.x_f_d = x_L - distance_follow_and_lead*math.cos(math.radians(theta_l))
        myclient.y_f_d = y_L - distance_follow_and_lead*math.sin(math.radians(theta_l))
        myclient.theta_f_d = theta_l
        myclient.cmd_f_d = cmd_L

        odom_string_f_d = "cmd_fd: {}\nx_fd: {:.2f}\ny_fd: {:.2f}\ntheta_fd: {:.2f}".format(myclient.cmd_f_d,myclient.x_f_d,myclient.y_f_d,myclient.theta_f_d)
        print(odom_string_f_d)
        count += 1
        #calculate PI here 
        vx = vx_PI.pi_output(myclient.x_f_d,myclient.xf_atc)
        vy = vy_PI.pi_output(myclient.y_f_d,myclient.yf_atc)
        # convert output to v and w 
        ############ maybe wrong
        v  = vx*math.cos(math.radians(myclient.thetaf_atc)) + vy * math.sin(math.radians(myclient.thetaf_atc)) 
        omega = (-vx*math.cos(math.radians(myclient.thetaf_atc)) + vy * math.sin(math.radians(myclient.thetaf_atc)))/(Radius_wheel)
        #calculate VR,VL
        v_R = (2*v + omega*L)/2
        v_L = (2*v - omega*L)/2
        data_vel_send_toMCU = "!cmd:{}#vr:{}#vl:{}#\n".format(myclient.cmd_f_d,v_R,v_L)
        print(data_vel_send_toMCU)
        #send data to mcu
        time.sleep(2)

def read_data_from_MCU():
    global myclient,vx,vy
    it = 0
    while True:

        #read data from MCu
        myclient.xf_atc+= vx*0.1
        myclient.yf_atc+= vy*0.1
        myclient.thetaf_atc = 45.00
        print("PI output{}\n".format(it))
        it+=1
        if data_fag == 0:
            break
        time.sleep(2)

def main():
    global myclient
    global client_socket
    thread1_recive_odom = threading.Thread(target=recieve_data_from_server)
    thread2_send_data_to_MCU = threading.Thread(target= read_data_from_MCU)
    thread1_recive_odom.start()
    thread2_send_data_to_MCU.start()
    # Let the main thread wait until the thread1_recive_odom finishes its job
    thread1_recive_odom.join()
    thread2_send_data_to_MCU.join()
    # close connection
    client_socket.close()
    
if __name__ == "__main__":
    main()
