import socket
import sys
import constants
import utilities as util

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    #client_socket.connect(("192.168.145.44", constants.TCP_PORT))
    client_socket.connect(("10.0.0.1", constants.TCP_PORT))
except:
    print("connection error")
    print(util.get_host_ip())
    sys.exit()

client_socket.send("lodinator".encode("utf8"))

if client_socket.recv(5120).decode("utf8") == "ack":
    print("received ack")

client_socket.close()
