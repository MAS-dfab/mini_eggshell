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

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()

    # now enter fabrication loop
    while True: # and ur and gh connected
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        print("continue_fabrication: %i" % continue_fabrication)
        if not continue_fabrication:
            break

        safe_pt_toggle = gh.wait_for_int()
        len_command = gh.wait_for_int()
        commands_flattened = gh.wait_for_float_list()
        # the commands are formatted according to the sent length
        commands = format_commands(commands_flattened, len_command)
        print("We received %i commands." % len(commands))



        if safe_pt_toggle:
            print("Moving to safe point")
            for i, cmd in enumerate(commands):
                if i == 0:
                    # Move to first point, toggle extruder and wait
                    x, y, z, ax, ay, az, speed, radius = cmd
                    ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
                    print("Toggling extruder")
                    ur.send_command_digital_out(0, True)

                    print("Waiting for 30 seconds")
                    ur.send_command_wait(30)

                    # And move axis
                    # p = s.SiemensPortal(1)
                    # p.set_x(650)
                    # p.set_z(850)


                else:
                    x, y, z, ax, ay, az, speed, radius = cmd
                    ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

        else:
            print("Skipping safe points")

            for i, cmd in enumerate(commands[1:-1]):
                    x, y, z, ax, ay, az, speed, radius = cmd
                    ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

        # for i, cmd in enumerate(commands):
        #     ur.wait_for_command_executed(i)
        #     print("Executed command", i+1, "of", len(commands), "[", (i+1)*100/(len(commands)), "%]")
        #     current_pose_cartesian = ur.get_current_pose_cartesian()
        #     print(current_pose_cartesian)

        ur.wait_for_ready()
        ur.send_command_digital_out(0, False)
        gh.send_float_list(commands[0])
        print("============================================================")
        """
        ur.wait_for_ready()
        # wait for sensor value
        digital_in = ur.wait_for_digital_in(number)
        current_pose_joint = ur.wait_for_current_pose_joint()
        current_pose_cartesian = ur.get_current_pose_cartesian()
        # send further to gh
        gh.send_float_list(digital_in)
        gh.send_float_list(current_pose_joint)
        gh.send_float_list(current_pose_cartesian)
        """
    ur.quit()
    gh.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
