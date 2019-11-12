from __future__ import print_function
from __future__ import absolute_import

import time
import sys
import json
from pathlib import Path

import socket


# Emmanuelle's
# python C:\Users\emman\Documents\GIT\mini_eggshell\ur_online_control\communication\main_direct_send_group_04.py
# Antons's
# python /c/Users/a/repos/mini_eggshell/ur_online_control/communcation/main_direct_send_group_04.py
# python C:\Users\a\repos\mini_eggshell\ur_online_control\communication\main_direct_send_group_04.py

# ===============================================================

# LOCAL LIBRARIES
# ===============================================================

FILE_DIR = Path(__file__).parent.absolute()
REPO_PATH = Path(__file__).parents[2].absolute()
sys.path.append(str(FILE_DIR))
sys.path.append(str(REPO_PATH))

from ur_online_control.communication.formatting import format_commands  # noqa: E402

# ===============================================================

# GLOBALS
# ===============================================================

FILE_NAME = "commands_group_04.json"
SERVER_ADRESS = "192.168.10.11"
SERVER_PORT = 30003
UR_IP = "192.168.10.10"
TOOL_ANGLE_AXIS = [-68.7916, -1.0706, 100, 3.1416, 0.0, 0.0]
AIR_PRESSURE_DO = 0
CLAY_EXTRUDER_DO = 4
UR_SERVER_PORT = 30002
DEBUG = True

# ===============================================================

# PARSE COMMANDS FROM JSON
# ===============================================================


def parse_json(file_name):
    file = Path.joinpath(FILE_DIR.parent, file_name)

    with file.open(mode='r') as f:
        data = json.load(f)

    start_at_safe_pt = data['start_at_safe_pt']
    len_command = data['len_command']
    gh_commands = data['gh_commands']

    commands = format_commands(gh_commands, len_command)

    validate_commands(commands)

    print("We have %d commands to send" % len(commands))

    return commands, start_at_safe_pt

# ===============================================================


def validate_commands(commands):
    for cmd in commands:
        x, y, z, ax, ay, az, speed, radius, travel = cmd

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert isinstance(ax, float)
        assert isinstance(ay, float)
        assert isinstance(az, float)
        assert isinstance(speed, (int, float))
        assert isinstance(radius, (int, float))
        assert isinstance(travel, (bool, str))

    print("GH commands validated")


# ===============================================================

# UR SCRIPT COMMANDS
# ===============================================================


def set_tcp():
    x, y, z, ax, ay, az = TOOL_ANGLE_AXIS
    return "\tset_tcp(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f])\n" % (x / 1000., y / 1000., z / 1000., ax, ay, az)

# ===============================================================


def movel_command(x, y, z, ax, ay, az, speed, radius):
    return "\tmovel(p[%.5f, %.5f, %.5f, %.5f, %.5f, %.5f], v=%f, r=%f)\n" % (x / 1000., y / 1000., z / 1000., ax, ay, az, speed / 1000., radius / 1000.)

# ===============================================================

# UR SCRIPT PROGRAMS
# ===============================================================


def generate_print_program(commands):
    script = ""
    script += "def program():\n"
    script += set_tcp()

    script += "\tset_digital_out(%i, True)\n" % (int(AIR_PRESSURE_DO))

    for i, cmd in enumerate(commands):

        # Make it backwards compatible with json-files without travel bool
        if len(cmd) != 9:
            cmd.append(False)

        x, y, z, ax, ay, az, speed, radius, travel = cmd

        # fix for weird json-schema and grasshopper
        if not isinstance(travel, bool):
            if travel == 'true'.lower():
                travel = True
            else:
                travel = False

        if travel:
            script += "\tset_digital_out(%i, false)\n" % (
                int(CLAY_EXTRUDER_DO))
            script += "\ttextmsg(\"Clay DO off\")\n"
            clay_DO = False

        script += movel_command(x, y, z, ax, ay, az, speed, radius)

        if not clay_DO:
            script += "\tset_digital_out(%i, true)\n" % (
                int(CLAY_EXTRUDER_DO))
            script += "\ttextmsg(\"Clay DO back on\")\n"
            clay_DO = True

        script += "\ttextmsg(\"Sending command number %d\")\n" % (i)

    script += "\tsocket_open(\"%s\", %d)\n" % (SERVER_ADRESS, SERVER_PORT)
    script += "\tsocket_send_string(\"c\")\n"
    script += "\tsocket_close()\n"
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================


def stop_extruder():
    script = ""
    script += "def program():\n"
    script += "\ttextmsg(\">> Turning of air pressure and extruder.\")\n"
    script += "\tset_digital_out(%i, False)\n" % (int(AIR_PRESSURE_DO))
    script += "\tset_digital_out(%i, False)\n" % (int(CLAY_EXTRUDER_DO))
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    return script

# ===============================================================


if __name__ == "__main__":

    commands, start_at_safe_pt = parse_json(FILE_NAME)

    send_socket = socket.create_connection((UR_IP, UR_SERVER_PORT), timeout=2)
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # extract safe_pt_command
    safe_pt_command = commands.pop(0)

    if start_at_safe_pt:
        script = generate_print_program(safe_pt_command)
        send_socket.send(script)
        # define optimum waiting time according to safe_pt position
        time.sleep(9)

    script = generate_print_program(commands)
    print("Sending commands")
    print(script.decode('utf-8'))

    # send file
    send_socket.send(script)

    # make server
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    recv_socket.bind((SERVER_ADRESS, SERVER_PORT))

    # Listen for incoming connections
    recv_socket.listen(1)
    while True:
        connection, client_address = recv_socket.accept()
        print("client_address", client_address)
        break

    recv_socket.close()

    script = stop_extruder()

    send_socket.send(script)

    print("Program done ...")
    time.sleep(5)

    send_socket.close()
