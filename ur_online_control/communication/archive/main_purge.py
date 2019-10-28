'''
Created on 22.11.2016
@author: rustr
'''

from __future__ import print_function
import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)


import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands

from eggshell_bh.linear_axis import siemens as s

#create logger to debug the code and check the speed and time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:    %(levelname)s:  %(message)s")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    #ur_ip = "192.168.10.11"
    ur_ip = "127.0.0.1"


def main():

    logger.info("\n\nlog started ,main is running\n")

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    logger.info("server started")

    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    logger.info("client wrappers created")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()

    logger.info("gh and ur are connected")


    continue_fabrication = gh.wait_for_int()
    print("continue_fabrication: %i" % continue_fabrication)


    move_filament_loading_pt = gh.wait_for_int()
    print("move_filament_loading_pt: %i" % move_filament_loading_pt)

    linear_axis_toggle = gh.wait_for_int()
    print("linear_axis_toggle: %i" % linear_axis_toggle)

    #if linear_axis_toggle:
    axis_moving_pts_indices = gh.wait_for_float_list()
    print("We received %i linear axis_moving_pts_indices" % len(axis_moving_pts_indices))

    logger.info("{} float list of axis_moving_pts_indices received".format(len(axis_moving_pts_indices)))

    len_command = gh.wait_for_int()
    print("len_command: %i" % len_command)

    no_batches = gh.wait_for_int()
    print("no_batches: %i" % no_batches)

    commands_to_wait_flattened = []

    for j in range(no_batches):
        commands_flattened = gh.wait_for_float_list()
        # create mew list for commands executed
        commands_to_wait_flattened.extend(commands_flattened)
        # the commands are formatted according to the sent length
        commands = format_commands(commands_flattened, len_command)
        print("We received %i commands." % len(commands))
        logger.info("{} float list of commands_flattened received".format(len(commands)))

        if move_filament_loading_pt:
        	commands_to_send = commands
        else:
        	commands_to_send = commands[1:-1]

        for i, cmd in enumerate(commands_to_send):
             x, y, z, ax, ay, az, speed, radius = cmd
             ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

        logger.info("all commands in batch number {} were sent".format(j))
        break

    print("=>>>>>>>>>>>>>>>>>>>>> wait for the 3rd")
    ur.wait_for_command_executed(3)


    ur.purge_commands()
    # ur.quit()
    # time.sleep(3)
    # ur.wait_for_connected()

    print("01_waiting for ready")
    # # time.sleep(1.5)
    ur.wait_for_ready()
    print("02 send new commands")
    # toggle extruder, turn off motor

    # move away robot problem: it still sends it at end
    x1, y1, z1, ax1, ay1, az1, speed1, radius1 = commands_to_send[0]
    ur.send_command_movel([x1, y1, z1, ax1, ay1, az1], v=speed1, r=radius1)
    print("03_Moving robot to a safe point")
    # print("Waiting for 10 seconds")
    # time.sleep(10)
    print("04_waiting for ready")
    ur.wait_for_ready()
    print("======================")

    ur.quit()
    gh.quit()
    # time.sleep(3)
    server.close()

    logger.info("siemens protal, gh, ur and server are closed")

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
