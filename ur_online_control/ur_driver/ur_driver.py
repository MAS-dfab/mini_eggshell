'''
Created on 22.11.2016

@author: rustr
'''
from __future__ import print_function

import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(parent_dir)
print(parent_dir)

import socket

is_py3 = True if sys.version_info[0] >= 3 else False


from ur_online_control.communication import msg_identifier_dict, command_identifier_dict
from ur_online_control.utilities import read_file_to_string, read_file_to_list

# https://www.universal-robots.com/how-tos-and-faqs/how-to/ur-how-tos/remote-control-via-tcpip-16496/
UR_SERVER_PORT = 30002

def generate_ur_program():
    """This function generates a program for the UR robot that allows for online
    communication.

    Returns:
        (string): the program as string
    """

    global msg_identifier_dict
    global command_identifier_dict

    path = os.path.join(os.path.dirname(__file__), "templates") # the path of the template files

    globals_file = os.path.join(path, "globals.urp")
    methods_file = os.path.join(path, "methods.urp")
    main_file = os.path.join(path, "main.urp")
    program_file = os.path.join(path, "program.urp")

    # source all files
    globals_list = read_file_to_list(globals_file)
    globals_str = "\t".join(globals_list)
    methods_list = read_file_to_list(methods_file)
    methods_str = "\t".join(methods_list)
    main_list = read_file_to_list(main_file)
    main_str = "\t".join(main_list)

    # globals
    iteritems = msg_identifier_dict.items() if is_py3 else msg_identifier_dict.iteritems()
    msg_identifier_str = "\n\t".join(["%s = %i" % (k, v) for k, v in iteritems])
    iteritems = command_identifier_dict.items() if is_py3 else command_identifier_dict.iteritems()
    command_identifier_str = "\n\t".join(["%s = %i" % (k, v) for k, v in iteritems])

    globals_str = globals_str.replace("{MESSAGE_IDENTIFIERS}", msg_identifier_str)
    globals_str = globals_str.replace("{COMMAND_IDENTIFIERS}", command_identifier_str)

    # program
    program_str = read_file_to_string(program_file)
    program_str = program_str.replace("{GLOBALS}", globals_str)
    program_str = program_str.replace("{METHODS}", methods_str)
    program_str = program_str.replace("{MAIN}", main_str)

    # strings that still have to be replaced
    # replace_list = ["{TOOL}", "{SERVER_ADDRESS}", "{PORT}", "{NAME}", "{NAME_LENGTH}"]
    return program_str

def send_script(ur_ip, script):
    global UR_SERVER_PORT
    try:
        s = socket.create_connection((ur_ip, UR_SERVER_PORT), timeout=2)
        s.send(script)
        print("Script sent to %s on port %i" % (ur_ip, UR_SERVER_PORT))
        s.close()
    except socket.timeout:
        print("UR with ip %s not available on port %i" % (ur_ip, UR_SERVER_PORT))
        raise

class URDriver(object):

    def __init__(self, server_ip, server_port, tool_angle_axis = [0,0,0,0,0,0], ip = "127.0.0.1", name = "UR"):

        program = generate_ur_program()

        tool_angle_axis_str = self._format_pose(tool_angle_axis)

        program = program.replace('{TOOL}', tool_angle_axis_str)
        program = program.replace('{SERVER_ADDRESS}', server_ip)
        program = program.replace('{PORT}', str(server_port))
        program = program.replace('{NAME}', name)
        program = program.replace('{NAME_LENGTH}', str(len(name)))

        self.program = program
        self.ip = ip


    def _format_pose(self, pose):
        mm2m = 1000.
        x, y, z, ax, ay, az = pose
        return "p[%.6f, %.6f, %.6f, %.4f, %.4f, %.4f]" % (x/mm2m, y/mm2m, z/mm2m, ax, ay, az)

    def send(self):
        send_script(self.ip, self.program)

    def __repr__(self):
        return self.program



class URDriver_3Dprint(object):

    def __init__(self, server_ip, server_port, tool_angle_axis = [0,0,0,0,0,0], ip = "127.0.0.1"):

        path = os.path.join(os.path.dirname(__file__), "templates") # the path of the template files
        filename = os.path.join(path, "ur_3dprinting_driver.urp")
        with open(filename, 'r') as f:
            program = f.read()

        tool_angle_axis_str = self._format_pose(tool_angle_axis)

        program = program.replace('{TOOL}', tool_angle_axis_str)
        program = program.replace('{SERVER_ADDRESS}', server_ip)
        program = program.replace('{PORT}', str(server_port))

        self.program = program
        self.ip = ip

    def _format_pose(self, pose):
        mm2m = 1000.
        x, y, z, ax, ay, az = pose
        return "p[%.6f, %.6f, %.6f, %.4f, %.4f, %.4f]" % (x/mm2m, y/mm2m, z/mm2m, ax, ay, az)

    def send(self):
        send_script(self.ip, self.program)

    def __repr__(self):
        return self.program



if __name__ == "__main__":

    server_ip = "192.168.10.2"
    server_port = 30003
    # tool_angle_axis = [0.0, 0.0, 115.6, 0.234, 1.57, 0.0]
    tool_angle_axis = [-68.791651245988589, -1.0706663314297771, 264.98184420337651, 3.1415926535897931, 0.0, 0.0]
    name = "UR"
    ur_ip = "192.168.10.13"

    #ur_driver = URDriver(server_ip, server_port, tool_angle_axis, ur_ip, name)
    ur_driver = URDriver_3Dprint(server_ip, server_port, tool_angle_axis, ur_ip)
    print(ur_driver)
    #ur_driver.send()
