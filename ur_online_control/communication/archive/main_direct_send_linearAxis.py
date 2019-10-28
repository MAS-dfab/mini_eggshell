from __future__ import print_function
from __future__ import absolute_import

import time
import sys
import os
import json

import socket
import os
import datetime

UR_SERVER_PORT = 30002

# python C:\Users\dfab\Documents\projects\ur_online_control\communication\main_direct_send_linearAxis.py
# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)

from ur_online_control.communication.formatting import format_commands
from eggshell_bh.linear_axis import siemens as s
#from eggshell_bh.phone import twilioComm as phoneAlert

from SocketServer import TCPServer, BaseRequestHandler
# ===============================================================
# GLOBALS
# ===============================================================
server_address = "192.168.10.2"
server_port = 30003
ur_ip = "192.168.10.13"
tool_angle_axis = [-68.7916, -1.0706, 264.9818, 3.1416, 0.0, 0.0]
# ===============================================================
# VARIABLES
# ===============================================================
linearAxis_base_x = 500 # mm
#linearAxis_base_z = 2200 # mm
#linearAxis_base_z = 1020 # mm
#linearAxis_base_z = 1602 # mm
#linearAxis_base_z = 1610 # mm
#linearAxis_base_z = 1615 # mm
linearAxis_base_z = 1620 # mm
#linearAxis_base_z = 1625 # mm
layers_to_move_linear_axis = 15
# ===============================================================
# COMMANDS
# ===============================================================
path = os.path.dirname(os.path.join(__file__))
filename = os.path.join(path, "..", "commands_1600_at_20.json")
with open(filename, 'r') as f:
    data = json.load(f)
# load the commands from the json dictionary
move_filament_loading_pt = data['move_filament_loading_pt']
linear_axis_toggle = data['move_linear_axis']
#points_per_layer = data['points_per_layer']
#layers_to_move_linear_axis = data['layers_to_move_linear_axis']
len_command = data['len_command']
gh_commands = data['gh_commands']
commands = format_commands(gh_commands, len_command)
print("We have %d commands to send" % len(commands))
# ===============================================================
# UR SCRIPT
# ===============================================================
def movel_commands(server_address, port, tcp, commands):
    script = ""
    script += "def program():\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x/1000., y/1000., z/1000., ax, ay, az)
    for i in range(len(commands)):
        x, y, z, ax, ay, az, speed, radius = commands[i]
        script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
        script += "\ttextmsg(\"sending command number %d\")\n" % (i) 
    script += "\tsocket_open(\"%s\", %d)\n" % (server_address, port)
    script += "\tsocket_send_string(\"c\")\n"
    script += "\tsocket_close()\n"
    script += "end\n"
    script += "program()\n\n\n"
    return script
# ===============================================================
def start_extruder(tcp, movel_command):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Start extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x/1000., y/1000., z/1000., ax, ay, az)
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
    script += "\tset_digital_out(0, True)\n"
    script += "end\n"
    script += "program()\n\n\n"
    return script
# ===============================================================
def stop_extruder(tcp, movel_command):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Stop extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x/1000., y/1000., z/1000., ax, ay, az)
    script += "\tset_digital_out(0, False)\n"
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
    script += "end\n"
    script += "program()\n\n\n"
    return script
# ===============================================================
def move_linearAxis(x_value,z_value):
    p = s.SiemensPortal(2)
    try:
        p.set_z(z_value)
        p.set_x(x_value)
        print("moving to Z =",z_value)
        print("moving to X =",x_value)
        #p. wait_ext_axis()
        pass
    except KeyboardInterrupt:
        print("stopping")
    finally:
        if p:
            p.close()
# ===============================================================
def get_linearAxis_z():
    p = s.SiemensPortal(2)
    try:
        zcoo = p.get_z()
        print("current linearAxis z coordinate =",zcoo)
        pass
    except KeyboardInterrupt:
        print("stopping")
    finally:
        if p:
            p.close()
    return zcoo
# ===============================================================

def main(commands):
    # number of points per layer
    points_per_layer = 264
    step = points_per_layer * layers_to_move_linear_axis

    send_socket = socket.create_connection((ur_ip, UR_SERVER_PORT), timeout=2)
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # move linear axis to initial base position
    if linear_axis_toggle:
        print ("moving linear axis to base ...")
        move_linearAxis(linearAxis_base_x, linearAxis_base_z)
        print("===========================================")
        time.sleep(2)

    if move_filament_loading_pt:
        first_command = commands[0]
        last_command = commands[-1]
        #script = start_extruder(tool_angle_axis, first_command)
        #send_socket.send(script)
        #time.sleep(60)

    commands = commands[1:-1]

    for i in range(0, len(commands), step):
        # get batch
        sub_commands = commands[i:i+step]
        print("length sub_commands %d " % (len(sub_commands)))
        script = movel_commands(server_address, server_port, tool_angle_axis, sub_commands)

        print("Sending commands %d to %d of %d in total." % (i + 1, i + step + 1, len(commands)))

        # send file
        send_socket.send(script)

        # make server
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the port
        recv_socket.bind((server_address, server_port))
        # Listen for incoming connections
        recv_socket.listen(1)

        print(datetime.datetime.now().time())
        
        while True:
            connection, client_address = recv_socket.accept()
            print("client_address", client_address)
            break
        recv_socket.close()
        
        print(datetime.datetime.now().time())

        failed = 0
        if linear_axis_toggle and i % step == 0:
            if move_filament_loading_pt:
                # ur move to safe_pt
                script = movel_commands(server_address, server_port, tool_angle_axis, [first_command])
                print("Moving linear axis and sending ur to safe point")
                send_socket.send(script)

            amount_z = ((i/step)+1)*layers_to_move_linear_axis
            linearAxis_move_amount = linearAxis_base_z + amount_z
            move_linearAxis(linearAxis_base_x,linearAxis_move_amount)
            # sleep time for the ur to move away till linear axis is positioned
            time.sleep(2)
            linear_axis_current_z = get_linearAxis_z()
            if linearAxis_move_amount == linear_axis_current_z:
                print ("SUCCESS! Linear axis moved to layer number {}".format(amount_z))
                print("===========================================")
            else:
                print ("FAILED! Linear axis didn't move to layer number {}".format(amount_z))
                print("===========================================")
                print("the print failed habibi. action: remove the filament, check latest command on ur panel, change gh layer selection end, export json, change base from python and resend ur ... Thanks for your attention")
                """ # alert if the print failed. action: check commands on panel, change gh layer selection end and resend ur
                numbers = {"nizar":"'+41768284582'", "joris":"'+41765135693'"}
                alert01 = PhoneContact()
                for key, value in numbers.items():
                    alert01.sendSms(value) """
                failed = 1

        if failed:
            break

    if move_filament_loading_pt:
        script = stop_extruder(tool_angle_axis, last_command)
        send_socket.send(script)
        time.sleep(1)

    send_socket.close()


if __name__ == "__main__":
    main(commands)
