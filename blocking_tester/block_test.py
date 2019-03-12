# alternate between removing and adding flows every N seconds

import sys
import requests
import argparse, sys
import ast
import json
import time

class blocker:
    def __init__(self, arguments):
        args = arguments
        self.interval = int(args.interval)
        self.block = args.block
        self.server_ip = args.server
        self.flag = True
        self.headers = {"Content-Type" : "application/json"}
        pass

    def block_test(self):

        print("blocker start")
        while(True):
            text = requests.get(self.server_ip).text    
            json_obj = json.loads(text)
            ip_list = ast.literal_eval(json_obj['address'])

            if self.flag:
                # add flow
                print("blocking " + self.block)
                ip_list.append(self.block)
            else:
                print("unblocking " + self.block)
                ip_list.remove(self.block)
                
            self.flag = not self.flag
            payload = {  'address' : ",".join(ip_list) }
            requests.put(self.server_ip, data=json.dumps(payload), headers=self.headers)
            time.sleep(self.interval)
        


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval', help='interval to cycle request', default='30')
    parser.add_argument('--block', help='IP to block', default='8.8.8.8')
    parser.add_argument('--server', help='server IP to retrieve from', default='http://localhost:8000/firewall/blockedips/1/?format=json')
    args=parser.parse_args()

    a = blocker(args)
    a.block_test()
