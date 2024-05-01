class odomerty_follower:
    def __init__(self, cmd, x, y, theta):
        self.cmd_f = cmd
        self.x_f = x
        self.y_f = y
        self.theta_f = theta


myclient = odomerty_follower("stp",0.00,0.00,0.00)
odom_string_f = "!cmd_f:{}#x_f{:.2f}:y_f:{:.2f}#theta_f:{:.2f}#\n".format(myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f)
print(odom_string_f)

myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f = "run",0.10,0.10,45.00
odom_string_f = "!cmd_f:{}#x_f{:.2f}:y_f:{:.2f}#theta_f:{:.2f}#\n".format(myclient.cmd_f,myclient.x_f,myclient.y_f,myclient.theta_f)
print(odom_string_f)
