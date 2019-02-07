import socket
import requests
import json
import sys
import object_class
import config
# json.load/json.dump -> for file-like objects
# json.loads/json.dumps -> for string streams
class main_handler():

    def __init__(self, user_object='user_basic'):
        # RETRIEVE AUTH TOKEN
        self.user_object = object_class.an_object(the_type=self.load_json_file(user_object))

        print(">RETRIEVING AUTH TOKEN")

        self.auth_token_message = message( json_data=self.user_object.dict_dump(),
                                           url=config.AUTH_TOKEN_URL,
                                           headers={'Content-Type':'application/json'} )
        self.auth_token = self.retrieve( self.auth_token_message.send_message('POST').text,
                                         config.AUTH_TOKEN_KEY )
        self.headers = {'Content-Type':'application/json', 'X-Auth-Token':self.auth_token}

        print("TOKEN RETRIEVAL DONE")


    def load_json_file(self, filename):
        try:
            with open('./jsonfiles/'+filename+'.json','r') as thefile:
                return json.load(thefile)
        except FileNotFoundError:
            raise FileNotFoundError("No such json file")
            sys.exit(1)

    def retrieve(self, json_stream, key):
        try:
            return json.loads(json_stream)[key]
        except KeyError:
            raise KeyError(str(key) + " was not found")

    # START OF FUNCTIONS FOR API CALL HANDLING

    # remote_activate_server -> just boots up the server with info specified at the server_type param (json file)
    def remote_activate_server(self, server_type='server_basic'):
        a = object_class.an_object(the_type=self.load_json_file(server_type))
        req = message( json_data=a.dump_dict(),
                       url=a.url,
                       headers={'Content-Type':'application/json',
                                'X-Auth-Token':self.auth_token} )
        req.send_message('POST')
        print(a.name + ' server up!')
        pass

    # add more API shit here in the future

class message():
    
    def __init__(self, **kwargs):
        
        try:
            self.data = kwargs['json_data']
            self.url = kwargs['url']
            self.headers = kwargs['headers']
        except KeyError:
            raise KeyError("missing params")


    def send_message(self, method):
        # CURL HELPER CLASS
        r = requests(method,self.url,data=self.data,headers=self.headers)
        if r.status_code != 200:
            print(str(r.status_code) + " error")
            sys.exit(1)
        return r       

