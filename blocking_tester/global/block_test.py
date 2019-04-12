# alternate between removing and adding flows every N seconds

import sys
import requests
import argparse, sys
import ast
import json
import time
from socket import *
import datetime

class blocker:
    def __init__(self, arguments):
        args = arguments
        self.interval = int(args.interval)
        self.block = args.block
        self.server_ip = args.server
        self.flag = True
        self.headers = {"Content-Type" : "application/json"}
        self.duration = int(args.duration) 

    def block_test(self):

        print("blocker start")
        ip_string = None
        for x in range(0,self.duration):
            if self.flag:
                print("blocking " + self.block)
                ip_string = self.block
            else:
                print("unblocking " + self.block)
                ip_string = "10.10.10.10"
            if x != 0:
                self.broadcast_signal("flags_block.txt")
            self.flag = not self.flag
            payload = {  'ip_address' : ip_string }

            requests.put(self.server_ip, data=json.dumps(payload), headers=self.headers)
            time.sleep(self.interval)
    def broadcast_signal(self, fname):
        f = open(fname,'a+')
        stringy = datetime.datetime.utcnow()
        stringy = str(stringy) + "\n"
        f.write(stringy)
        f.close()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval', help='interval to cycle request',
                        default='20')
    parser.add_argument('--duration', help='total interval steps', default='5')
    parser.add_argument('--block', help='IP to block', default='8.8.8.8')
    parser.add_argument('--server', help='server IP to retrieve from',
                        default='https://cs198globalcontroller.herokuapp.com/websites/7')
    args=parser.parse_args()

    a = blocker(args)
    a.block_test()
