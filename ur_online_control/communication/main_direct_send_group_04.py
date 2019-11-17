from __future__ import print_function
from __future__ import absolute_import

import json
import logging
from pathlib import Path
import socket
import sys
import time


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
UR_SERVER_PORT = 30002
TOOL_ANGLE_AXIS = [-68.7916, -1.0706, 100, 3.1416, 0.0, 0.0]
AIR_PRESSURE_DO = 0
CLAY_EXTRUDER_DO = 4

# ===============================================================

# UTIL
# ===============================================================

LOG_FILE = Path.joinpath(FILE_DIR, "main_direct_send_group_04.log")
UR_SCRIPT_LOG = Path.joinpath(FILE_DIR, "main_direct_send_group_04.ur_log.log")
logging.basicConfig(filename=LOG_FILE, filemode='a', level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(funcName)s:%(message)s")


def start_log() -> None:
    logging.debug("Start script")
    logging.debug("GLOBALS")
    logging.debug("FILE_DIR: {}".format(FILE_DIR))
    logging.debug("REPO_PATH: {}".format(REPO_PATH))
    logging.debug("FILE_NAME: {}".format(FILE_NAME))
    logging.debug("SERVER_ADRESS: {}".format(SERVER_ADRESS))
    logging.debug("SERVER_PORT: {}".format(SERVER_PORT))
    logging.debug("UR_IP: {}".format(UR_IP))
    logging.debug("UR_SERVER_PORT: {}".format(UR_SERVER_PORT))
    logging.debug("TOOL_ANGLE_AXIS: {}".format(TOOL_ANGLE_AXIS))
    logging.debug("AIR_PRESSURE_DO: {}".format(AIR_PRESSURE_DO))
    logging.debug("CLAY_EXTRUDER_DO: {}".format(CLAY_EXTRUDER_DO))

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

    #validate_commands(commands)

    print("We have %d commands to send" % len(commands))

    return commands, start_at_safe_pt

# ===============================================================


def validate_commands(commands):
    for cmd in commands:

        # backwards compability
        try:
            x, y, z, ax, ay, az, speed, radius, travel = cmd
        except ValueError:
            x, y, z, ax, ay, az, speed, radius = cmd

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert isinstance(ax, float)
        assert isinstance(ay, float)
        assert isinstance(az, float)
        assert isinstance(speed, (int, float))
        assert isinstance(radius, (int, float))

        # only test travel if command has travel bools
        if 'travel' in locals():
            assert isinstance(travel, (bool, str))

    logging.debug("GH commands validated")


# ===============================================================

# UR SCRIPT COMMANDS
# ===============================================================


def set_tcp() -> str:
    x, y, z, ax, ay, az = TOOL_ANGLE_AXIS
    cmd = "set_tcp(p[{:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}])".format(
        x/1000., y / 1000., z / 1000., ax, ay, az)
    return add_whitespace(cmd)

# ===============================================================


def movel(x, y, z, ax, ay, az, speed, radius) -> str:
    cmd = "movel(p[{:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}, {:.5f}], v={:.3f}, r={:.3f})".format(
        x/1000., y / 1000., z / 1000., ax, ay, az, speed / 1000., radius / 1000.)
    return add_whitespace(cmd)

# ===============================================================


def textmsg(string: str) -> str:
    cmd = "textmsg(\"" + string + "\")"
    return add_whitespace(cmd)

# ===============================================================


def set_DO(pin: int, state: bool) -> str:
    cmd = "set_digital_out({:d}, {})".format(pin, state)
    return add_whitespace(cmd)

# ===============================================================


def sleep(seconds: int) -> str:
    cmd = "sleep({})".format(seconds)
    return add_whitespace(cmd)

# ===============================================================


def popup(string: str) -> str:
    # Popup title not implemented, neither is error or warning flags
    cmd = "popup(\"{}\")".format(string)
    return add_whitespace(cmd)

# ===============================================================


def add_whitespace(string: str) -> str:
    return "\t" + string + "\n"


# ===============================================================

# UR SCRIPT PROGRAMS
# ===============================================================


def generate_print_program(commands):
    clay_DO = False
    script = ""
    script += "def program():\n"
    script += set_tcp()

    script += set_DO(AIR_PRESSURE_DO, True)
    script += textmsg("Air pressure on")

    # uncomment two following lines if it takes too long to get the air
    # pressure spread through whole setup:
    # script += sleep(5)
    # script += textmsg("Sleeping 5 seconds.")

    for i, cmd in enumerate(commands):

        # Make it backwards compatible with json-files without travel bool
        if len(cmd) != 9:
            cmd.append(False)
            logging.debug("No travel bool in json, defaults to False")

        x, y, z, ax, ay, az, speed, radius, travel = cmd

        # fix for weird json-schema and grasshopper
        if not isinstance(travel, bool):
            if travel == 'true'.lower():
                travel = True
            else:
                travel = False

        if travel:
            script += set_DO(CLAY_EXTRUDER_DO, False)
            script += textmsg("Clay DO off")
            clay_DO = False

        script += movel(x, y, z, ax, ay, az, speed, radius)

        if not clay_DO:
            script += set_DO(CLAY_EXTRUDER_DO, True)
            script += textmsg("Clay DO back on")
            clay_DO = True

        script += textmsg("Sending command number: {:d}".format(i))

    script += "\tsocket_open(\"%s\", %d)\n" % (SERVER_ADRESS, SERVER_PORT)
    script += textmsg("End program")
    script += "\tsocket_send_string(\"c\")\n"
    script += "\tsocket_close()\n"
    script += "end\n"
    script += "program()\n\n\n"

    script = script.encode()

    with open(UR_SCRIPT_LOG, mode='w') as f:
        f.write(script.decode('utf-8'))

    return script

# ===============================================================


def stop_extruder():
    script = ""
    script += "def program():\n"
    script += textmsg("Turning of air pressure and extruder.")
    script += set_DO(AIR_PRESSURE_DO, False)
    script += set_DO(CLAY_EXTRUDER_DO, False)
    script += "end\n"
    script += "program()\n\n\n"
    script = script.encode()
    logging.debug("Stop extruder function ran")
    return script

# ===============================================================


def main() -> None:
    start_log()

    commands, start_at_safe_pt = parse_json(FILE_NAME)

    send_socket = socket.create_connection((UR_IP, UR_SERVER_PORT), timeout=2)
    send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    logging.debug("Sockets setup")

    # extract safe_pt_command
    safe_pt_command = commands.pop(0)

    if start_at_safe_pt:
        script = generate_print_program(safe_pt_command)
        send_socket.send(script)
        # define optimum waiting time according to safe_pt position
        time.sleep(9)

    script = generate_print_program(commands)
    print("Sending commands")

    # send file
    send_socket.send(script)
    logging.debug("File sent")

    # make server
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    recv_socket.bind((SERVER_ADRESS, SERVER_PORT))

    # Listen for incoming connections
    recv_socket.listen(1)
    while True:
        logging.debug("Waiting for accept")
        connection, client_address = recv_socket.accept()
        logging.debug("Recieved accept from: {}".format(client_address))
        break

    recv_socket.close()

    script = stop_extruder()

    send_socket.send(script)

    time.sleep(5)

    send_socket.close()
    print("Program done ...")


if __name__ == "__main__":
    main()
