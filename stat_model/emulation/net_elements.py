import socket
from threading import Thread
import constants
import sys
import time


# network element classes for extendable code
# use these helper classes when spawning threads


# Client class spawned for every Source IP
class Client:
    def __init__(self, *args, **kwargs):
        self.address = None
        self.packet_list = None
        for key, value in self.__dict__.items():
            try:
                self.__dict__[key] = kwargs[key]
            except:
                raise KeyError(key + " attribute not specified!")
        self.destinations = {}

    def activate(self):
        # start a new thread of process to continue
        Thread(target=self.process_packets, args=[]).start()

    def process_packets(self):
        the_threads = []
        for packet in self.packet_list:
            index = packet.dst_ip
            self.destinations.setdefault(index, []).append(packet)

        for key, value in self.destinations.items():
            # thread for each destination
            x = Thread(target=self.send_all, args=(key, value))
            x.start()
            the_threads.append(x)

        # WAIT FOR ALL THREADS TO FINISH    
        for x in the_threads:
            x.join()

        print("ALL PACKETS SENT")

                
    def send_all(self, destination_IP, packet_list):
        # client connect send many

        counter = 0
        while counter < len(packet_list):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                client_socket.connect((destination_IP, constants.TCP_PORT))
            except:
                print("connection error")
                sys.exit()

            print(len(packet_list))
            the_list = packet_list[counter:]
            for packet in the_list:
                # THIS LINE CREATES A STRING OF sys.getsize() = packet.payload_size
                counter = counter + 1
                the_size = packet.payload_size
                if the_size < 50:
                    the_size = 50
                the_payload = str("x" * (the_size -49))
                # 49 IS A PYTHONIC OFFSET
                ender = str(packet.connection_ender)
                if counter == len(packet_list):
                    ender = "True"
                data = the_payload + ',' + str(packet.response_size) + ',' +  str(packet.delay) + ',' + ender 
                print(data)
                # TIMESTAMP GOES HERE
                client_socket.send(data.encode("utf8"))

                if len(client_socket.recv(40000).decode("utf8")) > 0:
                    print("received ack")
                    pass        # null operation

                if ender == 'True':
                    break
                # CHECK TIMESTAMP HERE
            client_socket.close()

# packet helper class so serializing would be easier
class Packet:
    def __init__(self, **kwargs):
        self.delay = 0
        # src_ip possible redundancy
        self.src_ip = None
        self.dst_ip = None
        self.payload_size = 0
        self.response_size = 0
        self.connection_ender = False
        for key, value in self.__dict__.items():
            try:
                self.__dict__[key] = kwargs[key]
            except:
                raise KeyError(key + " attribute not specified!")


# server class spawned for every destination IP
class Server:
    def __init__(self, **kwargs):
        # make some for udp and TCP soon
        self.IP_address = None

        try:
            self.IP_address = kwargs['address']
        except:
            raise KeyError("no IP address set")
            
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
        try:
            self.server_socket.bind((self.IP_address, constants.SERVER_HOST_PORT))
        except:
            print("Bind failed. Error : " + str(sys.exc_info()))
            sys.exit()
    
    def start_socket(self):
        
        self.server_socket.listen(constants.MAX_CONNECTIONS)       # queue up to 5 requests
        print("Socket now listening")

        # infinite loop- do not reset for every requests
        while True:
            connection, address = self.server_socket.accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with " + ip + ":" + port)

            try:
                Thread(target=self.client_thread, args=(connection, ip, port)).start()
            except:
                print("Thread did not start.")
                traceback.print_exc()
        self.server_socket.close()


    def client_thread(self, connection, ip, port, max_buffer_size=40000):
        is_active = True

        while is_active: 
            response_size, delay_time, ender = self.receive_input(connection, 40000)

            if ender == 'True':
                print("Client is requesting to quit")
                connection.close()
                print("Connection " + ip + ":" + port + " closed") 
                is_active = False
            else:
                #print("Processed result: {}".format(client_input)) 
                print("acknowledging ")
                the_size = int(response_size)
                if the_size < 50:
                    the_size = 50
                the_payload = str("x" * (the_size - 49 - 15)) + "acknowledgement"

                # 49 IS A PYTHONIC OFFSET
                # 15 is for the "acknowledgement" string
                connection.sendall(the_payload.encode("utf8"))

                #connection.sendall("ack".encode("utf8"))


    def receive_input(self, connection, max_buffer_size):
        client_input = connection.recv(max_buffer_size)

        # DEAL WITH FRAGMENTATION
        while client_input.decode("utf-8")[-1:] != 'e':
            print(client_input.decode("utf-8"))
            packet = connection.recv(max_buffer_size)
            if not packet:
              break
            client_input += packet

        client_input_size = sys.getsizeof(client_input)
        if client_input_size > max_buffer_size:
            print("The input size is greater than expected {}".format(client_input_size))

        decoded_input = client_input.decode("utf8").rstrip()
        print(decoded_input)
        result = self.process_input(decoded_input)

        return result


    def process_input(self,input_str):
        print("Processing the input received from client")
        try:
            final_strings = input_str.split(",")
            # OUTPUT: PAYLOAD         RESPONSE SIZE      RESPONSE DELAY  ENDER
            time.sleep(float(final_strings[2]))
            return final_strings[1], final_strings[2], final_strings[3]
        except:
            # send a quit packet
            print(str(input_str))
            raise ValueError("input does not follow packet format")
        return None,None,'True'

