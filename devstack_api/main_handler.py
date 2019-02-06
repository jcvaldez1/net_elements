import socket
import requests
import json
import sys

# json.load/json.dump -> for file-like objects
# json.loads/json.dumps -> for string streams
class main_handler():

    def __init__(self):
        # RETRIEVE AUTH TOKEN
        self.auth_token_message = message( json_data=config.AUTH_TOKEN_JSON_FNAME,
                                           url=config.AUTH_TOKEN_URL,
                                           headers={'Content-Type':'application/json'} )

        self.auth_token = self.retrieve(self.auth_token_message.send_message(),
                                        config.AUTH_TOKEN_KEY)


        # RETREIVE ACCESS TOKEN
        self.access_token_message = message( json_data=config.ACCESS_TOKEN_JSON_FNAME,
                                             url=config.ACCESS_TOKEN_URL,
                                             headers={'Content-Type':'application/json',
                                                      'X-Auth-Token':self.auth_token} )

        self.access_token = self.retrieve(self.access_token_message.send_message(),
                                          config.ACCESS_TOKEN_KEY)


    def load_json_file(self, filename):
        try:
            with open(filename,'r') as thefile:
                return json.load(thefile)
        except FileNotFoundError:
            raise FileNotFoundError("No such filename")
            #print("No such filename")
            sys.exit(1)

    def retrieve(self, json_stream, key):
        try:
            return json.loads(json_stream)[key]
        except KeyError:
            raise KeyError(str(key) + " was not found")

    def remote_activate():
        pass


class message():
    
    def __init__(self, **kwargs):
        
        try:
            self.data = kwargs['json_data']
            self.url = kwargs['url']
            self.headers = kwargs['headers']
        except KeyError:
            raise KeyError("missing params")


    def send_message(self):
        # CURL HELPER CLASS
        r = requests.get(self.url,data=self.data,headers=self.headers)
        if r.status_code != 200:
            print(str(r.status_code) + " error")
            sys.exit(1)
        return r.text()        

