from __future__ import print_function
from __future__ import absolute_import

import time
import sys
import os
import json

import socket

UR_SERVER_PORT = 30002

# python path to your file....\ur_online_control\communication\main_direct_send_group_00.py
# python C:\Users\indra\Documents\GIT\mini_eggshell\ur_online_control\communication\main_direct_send_group_03.py

# set the paths to find library
file_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)

from ur_online_control.communication.formatting import format_commands

# GLOBALS
# ===============================================================
server_address = "192.168.10.11"
server_port = 30003
ur_ip = "192.168.10.13"

# UR 5 for 50mm nozel height (300mm table setup)
# tool_angle_axis = [-68.7916, -1.0706, 132, 3.1416, 0.0, 0.0]

# UR 5 for 112mm nozel height (300mm table setup)
# tool_angle_axis = [-68.7916, -1.0706, 194, 3.1416, 0.0, 0.0]

# UR 10 for 50mm nozel height (300mm table setup)
# tool_angle_axis = [-68.7916, -1.0706, 112, 3.1416, 0.0, 0.0]


# UR 10 for 112mm nozel height (300mm table setup)
# tool_angle_axis = [-68.7916, -1.0706, 110, 3.1416, 0.0, 0.0]


# UR 10 for 112mm nozel height (787 mm table setup)
# tool_angle_axis = [30, -62, 118, 3.1416, 0.0, 0.0]

# UR 10 for 50mm nozel height (787 mm table setup)
# tool_angle_axis = [30, -62, 55, 3.1416, 0.0, 0.0]

# UR 10 for 97mm nozel height (787 mm table setup)
tool_angle_axis = [30, -62, 105, 3.1416, 0.0, 0.0]

# ===============================================================

# COMMANDS
# ===============================================================
path = os.path.dirname(os.path.join(__file__))
filename = os.path.join(path, "..", "commands_group_03.json")
with open(filename, 'r') as f:
    data = json.load(f)
# load the commands from the json dictionary
move_filament_loading_pt = data['move_filament_loading_pt']
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
    script = script.encode()
    return script

# ===============================================================
def start_extruder(tcp, movel_command, digital_output):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Start extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x/1000., y/1000., z/1000., ax, ay, az)
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
    script += "\tset_digital_out(%i, True)\n" % (int(digital_output))
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================
def stop_extruder(tcp, movel_command, digital_output):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Stop extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x/1000., y/1000., z/1000., ax, ay, az)
    script += "\tset_digital_out(%i, False)\n" % (int(digital_output))
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================
def main(commands):
    send_socket = socket.create_connection((ur_ip, UR_SERVER_PORT), timeout=2)
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # define i/o digital output numbers
    air_pressure_DO = 0
    clay_extruder_motor_DO = 4
    #
    # plastic_extruder_motor_DO = 0
    # plastic_extruder_fan_DO = 0

    if move_filament_loading_pt:
        first_command = commands[0]
        second_command = commands[1]
        last_command = commands[-1]
        script = start_extruder(tool_angle_axis, first_command, air_pressure_DO)
        send_socket.send(script)
        # define optimum waiting time according to safe_pt position
        time.sleep(60)
        script = start_extruder(tool_angle_axis, first_command, clay_extruder_motor_DO)
        send_socket.send(script)

    # commands without filament loading points
    commands = commands[1:-1]

    script = movel_commands(server_address, server_port, tool_angle_axis, commands)
    print("sending commands ...")

    # send file
    send_socket.send(script)

    # make server
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    recv_socket.bind((server_address, server_port))
    # Listen for incoming connections
    recv_socket.listen(1)
    while True:
        connection, client_address = recv_socket.accept()
        print("client_address", client_address)
        break
    recv_socket.close()

    if move_filament_loading_pt:
        # script = stop_extruder(tool_angle_axis, last_command, air_pressure_DO)
        script = stop_extruder(tool_angle_axis, last_command, clay_extruder_motor_DO)
        send_socket.send(script)
        time.sleep(1)

    send_socket.close()
    print ("program done ...")


if __name__ == "__main__":
    main(commands)
