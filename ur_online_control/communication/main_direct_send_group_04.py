from __future__ import print_function
from __future__ import absolute_import

import time
import sys
import os
import json

import socket

UR_SERVER_PORT = 30002

# Emmanuelle's
# python C:\Users\emman\Documents\GIT\mini_eggshell\ur_online_control\communication\main_direct_send_group_04.py
# python C:\Users\a\repos\mini_eggshell\ur_online_control\communication\main_direct_send_group_04.py
# Antons's
# python /c/Users/a/repos/mini_eggshell/ur_online_control/communcation/main_direct_send_group_04.py
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
ur_ip = "192.168.10.10"
tool_angle_axis = [-68.7916, -1.0706, 100, 3.1416, 0.0, 0.0]
# ===============================================================

# COMMANDS
# ===============================================================
path = os.path.dirname(os.path.join(__file__))
filename = os.path.join(path, "..", "commands_group_04.json")
with open(filename, 'r') as f:
    data = json.load(f)
# load the commands from the json dictionary
start_at_safe_pt = data['start_at_safe_pt']
len_command = data['len_command']
gh_commands = data['gh_commands']
commands = format_commands(gh_commands, len_command)
print("We have %d commands to send" % len(commands))
# ===============================================================

# UR SCRIPT
# ===============================================================


def movel_commands(server_address, port, tcp, commands, air_pressure_DO, clay_extruder_motor_DO):
    clay_DO = False

    script = ""
    script += "def program():\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x /
                                                                      1000., y/1000., z/1000., ax, ay, az)
    script += "\tset_digital_out(%i, True)\n" % (int(air_pressure_DO))
    for i in range(len(commands)):
        x, y, z, ax, ay, az, speed, radius, travel = commands[i]
        if travel and clay_DO:
            script += "\tset_digital_out(%i, false)\n" % (
                int(clay_extruder_motor_DO))
            clay_DO = False
            script += "\ttextmsg(\"Clay DO off\")\n"
        elif not clay_DO:
            script += "\tset_digital_out(%i, true)\n" % (
                int(clay_extruder_motor_DO))
            clay_DO = True
            script += "\ttextmsg(\"Clay DO on\")\n"

        script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (
            x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)

        script += "\ttextmsg(\"sending command number %d\")\n" % (i)

    script += "\tsocket_open(\"%s\", %d)\n" % (server_address, port)
    script += "\tsocket_send_string(\"c\")\n"
    script += "\tsocket_close()\n"
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================


def movel_safe_pt(tcp, movel_command):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Start extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x /
                                                                      1000., y/1000., z/1000., ax, ay, az)
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (
        x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================


def stop_extruder(tcp, movel_command, air_pressure_DO, clay_extruder_motor_DO):
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Stop extruder.\")\n"
    x, y, z, ax, ay, az = tcp
    script += "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x /
                                                                      1000., y/1000., z/1000., ax, ay, az)
    script += "\tset_digital_out(%i, False)\n" % (int(air_pressure_DO))
    script += "\tset_digital_out(%i, False)\n" % (int(clay_extruder_motor_DO))
    x, y, z, ax, ay, az, speed, radius = movel_command
    script += "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (
        x/1000., y/1000., z/1000., ax, ay, az, speed/1000., radius/1000.)
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

    last_command = commands[-1]

    if start_at_safe_pt:
        first_command = commands[0]
        script = movel_safe_pt(tool_angle_axis, first_command)
        send_socket.send(script)
        # define optimum waiting time according to safe_pt position
        time.sleep(9)
        send_socket.send(script)
    # commands with safe_pt removed
    commands = commands[1:-1]

    script = movel_commands(server_address, server_port, tool_angle_axis,
                            commands, air_pressure_DO, clay_extruder_motor_DO)
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

    script = stop_extruder(tool_angle_axis, last_command,
                           air_pressure_DO, clay_extruder_motor_DO)
    send_socket.send(script)
    print("program done ...")
    time.sleep(30)

    send_socket.close()


if __name__ == "__main__":
    main(commands)
