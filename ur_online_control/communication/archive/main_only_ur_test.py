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

from ur_online_control.ur_direct import stop as stop_robot

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
    ur = ClientWrapper("UR")

    logger.info("client wrappers created")

    # wait for the clients to be connected
    ur.wait_for_connected()

    logger.info("ur is connected")

    # now enter fabrication loop
    while True: # and ur and gh connected
        commands_to_send = [[i] * 8 for i in range(20)]
            
        for i, cmd in enumerate(commands_to_send):
            x, y, z, ax, ay, az, speed, radius = cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

        time.sleep(4)
        ur.purge_commands()
        print("waiting for ready")
        ur.wait_for_ready()
        print("send new commands")
        for i, cmd in enumerate(commands_to_send):
            x, y, z, ax, ay, az, speed, radius = cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
        print("============================================================")

    ur.quit()
    server.close()

    logger.info("siemens protal, gh, ur and server are closed")

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
