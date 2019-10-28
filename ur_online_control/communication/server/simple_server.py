from __future__ import print_function

import struct
import sys
import socket
import select
import time
from threading import Thread
from Queue import Queue

MSG_QUIT = 16
MSG_MOVEL = 2
MSG_MOVEL_EXECUTED = 5

class SimpleServer(object):
    """
    """
    def __init__(self, address='127.0.0.1', port=30003):
        self.address = address
        self.port = port
        self.server = None
        self.input = []
        self.running = True
        self.clients = []
    
    def start(self):
        self.running_thread = Thread(target = self.run)
        self.running_thread.daemon = False
        self.running_thread.start()

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        self.server.listen(1)
        self.input = [self.server]
        print("Server running on address %s and port %d." % (self.address, self.port))

        timeout = 0.008

        while self.running:
            try:
                inputready, outputready, exceptready = select.select(self.input, [], [], timeout)
            except socket.error as e:
                if e.errno == socket.errno.EBADF: # raise error(EBADF, 'Bad file descriptor')
                    pass
                else:
                    raise
            except select.error:
                print("An operation was attempted on something that is not a socket")

            for s in inputready:
                if s == self.server:
                    try:
                        sock, address = self.server.accept()
                        ip, port = address
                        print("Incoming connection from %s, at port %d. " % (ip, port))
                        self.input.append(sock)
                        client_socket = SimpleClient(sock, ip)
                        client_socket.start()
                        self.clients.append(client_socket)
                    except socket.error as e:
                        break
                elif s == sys.stdin: # close on key input
                    # handle standard input
                    junk = sys.stdin.readline()
                    print(junk)
                    break
        self.server.close()
    
    def close(self):
        self.running = False
        self.server.close()
        self.running_thread.join()

class SimpleClient(object):
    """
    """

    MULT = 100000.0 # for converting the integers to floats

    def __init__(self, socket, ip):
        self.socket = socket
        self.ip = ip
        self.msg_rcv = ""
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        self.byteorder_isset = False

        self.running = True
        self.socket.settimeout(0.008)
        self.snd_queue = Queue()
        self.counter = 0

    def read(self):
        """
        """
        # The transmission protocol for messages is
        # [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]

        # 1. read msg length
        self.msg_rcv += self.socket.recv(4)

        if len(self.msg_rcv) < 4:
            return
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]

        # TODO: how to check this better?
        if not self.byteorder_isset:
            msg_length2 = socket.ntohl(msg_length) # convert 32-bit positive integers from network to host byte order
            if msg_length2 < msg_length:
                self.byteorder = "<"
                msg_length = msg_length2
            self.byteorder_isset = True

        # 2. read msg according to msg_length
        self.msg_rcv += self.socket.recv(msg_length)
        if len(self.msg_rcv) < (msg_length + 4):
            return
        
        while len(self.msg_rcv) >= 8:

            # 3. message identifier
            msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[4:8], 0)[0]

            #print("Received %i ==>" % msg_length)
            #print("Received %i ==>" % msg_id)

            # 4. rest of message, according to msg_length
            raw_msg = self.msg_rcv[8:(8 + msg_length - 4)]

            # 5. set self.msg_rcv to the rest
            self.msg_rcv = self.msg_rcv[(8 + msg_length - 4):]

            #print("raw_msg", len(raw_msg))
            #print("self.msg_rcv", len(self.msg_rcv))

            # 4. pass message id and raw message to process method
            if msg_id == MSG_MOVEL_EXECUTED:
                self.counter += 1
                # try sending next
                if not self.snd_queue.empty():
                    msg_id, cmd = self.snd_queue.get()
                    #print("Commands to go:", self.snd_queue.qsize())
                    self.send(MSG_MOVEL, cmd)
            else:
                print("msg_id %d not recognized" % msg_id)
                print(raw_msg)
        
       


    def send(self, msg_id, msg = None):
        # The transmission protocol for send messages is
        # [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]

        buf = None

        if msg_id == MSG_QUIT:
            # print("formatting quit")
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)

        elif msg_id == MSG_MOVEL:
            # UR: [x, y, z, ax, ay, az, acc, speed, radius, time]
            cmd = msg
            print("Sending", cmd)
            msg_command_length = 4 * (len(cmd) + 1) # + msg_id
            cmd = [c * self.MULT for c in cmd]
            params = [msg_command_length, msg_id] + cmd
            buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        else:
            print("msg_id unknown")
            return

        # send buf
        try:
            self.socket.send(buf)
            #print("Sent message %i." % msg_id)

        except socket.timeout:
            print("Timeout in sending, trying again...")
            time.sleep(0.5)
            self.socket.send(buf)
            #print("Sent message %i." % msg_id)

        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053:
                self.running = False

    def start(self):
        self.running_thread = Thread(target = self.run)
        self.running_thread.daemon = True # die if main dies
        self.running_thread.start()

    def run(self):
        while self.running:
            try:
                self.read()
            except socket.timeout:
                pass # time outs are allowed
            except socket.error as e:
                if e.errno == socket.errno.WSAECONNRESET: # An existing connection was forcibly closed by the remote host
                    print("Client is not available anymore.")
                    self.running = False
                    break
        self.socket.close()