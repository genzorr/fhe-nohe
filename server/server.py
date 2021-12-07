#!/usr/bin/env python3
import sys
import socket
import errno
from time import sleep
from nohe.packet import Packet
from nohe.nohe import Functions

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65534  # Port to listen on (non-privileged ports are > 1023)

while True:
    print('Opening socket')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        sock, addr = s.accept()
        print(f'Connected to client {HOST}:{PORT}')
        with sock:
            while True:
                dataRecv = None
                try:
                    dataRecv = sock.recv(Packet.maxSize)
                except socket.error as e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        sleep(1)
                        continue
                    else:
                        print(f'Socket error occured: {e}')
                        break
                else:
                    if dataRecv and dataRecv != b'':
                        print(f'Received packet {dataRecv}')

                        # Extract operation, X, Y from received data
                        packet = Packet()
                        op, encX, encY = packet.from_bytes(dataRecv)

                        # Perform operation
                        nohe_f = Functions(encX, encY)
                        dataSend = None
                        if op == 'XOR':
                            dataSend = nohe_f.nohe_xor()
                        elif op == 'AND':
                            dataSend = nohe_f.nohe_and()

                        sock.sendall(dataSend)
                        print(f'Sent result {dataSend}')
