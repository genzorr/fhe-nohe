#!/usr/bin/env python3
import sys
import socket
import errno
from time import sleep
from nohe.packet import ClientPacket, ServerPacket
from nohe.nohe import Functions

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65534  # Port to listen on (non-privileged ports are > 1023)

print('Opening socket')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

while True:
    try:
        sock, addr = s.accept()
        print()
        print(f'Connected to client {HOST}:{PORT}')
    except socket.error as e:
        print(f'Socket error: {e}')
    else:
        while True:
            dataRecv = None
            try:
                dataRecv = sock.recv(ClientPacket.maxSize)
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
                    print(f'Received packet: {dataRecv}')

                    # Extract operation, X, Y from received data
                    packet = ClientPacket()
                    op, encX, encY = packet.from_bytes(dataRecv)
                    print(f'Received data: op = {op}, encX = {encX}, encY = {encY}')

                    # Perform operation
                    plain_res, nohe_res = None, None
                    nohe_f = Functions(encX, encY)
                    if op == 'XOR':
                        plain_res = nohe_f.plain_xor()
                        nohe_res = nohe_f.nohe_xor()
                    elif op == 'AND':
                        plain_res = nohe_f.plain_and()
                        nohe_res = nohe_f.nohe_and()
                    print(f'Encoded result: Z1 = {plain_res}, Z2 = {nohe_res}')

                    # Create packet
                    packet = ServerPacket(plain_res, nohe_res)
                    dataSend = packet.to_bytes()
                    sock.sendall(dataSend)
                    print(f'Sent packet: {dataSend}')
                    break
