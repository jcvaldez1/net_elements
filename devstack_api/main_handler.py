import socket
import requests
import json
import sys
import object_class
import config
import time
# json.load/json.dump -> for file-like objects
# json.loads/json.dumps -> for string streams
class main_handler():

    def __init__(self, user_object='user_basic'):
        # RETRIEVE AUTH TOKEN
        self.user_object = object_class.an_object(the_type=self.load_json_file(user_object))

        print(">RETRIEVING AUTH TOKEN")

        self.auth_token_message = message(
            json_data=json.dumps(self.user_object.dump_dict()),
                                           url=self.user_object.url,
                                           headers={'Content-Type':'application/json'} )
        self.auth_token = self.retrieve(
            self.auth_token_message.send_message('POST').headers,
                                         config.AUTH_TOKEN_KEY )
        self.headers = {'Content-Type':'application/json', 'X-Auth-Token':self.auth_token}

        print("TOKEN RETRIEVAL DONE")

        self.public_access_ip = None

    def load_json_file(self, filename):
        try:
            with open('/home/thesis/net_elements/devstack_api/jsonfiles/'+filename+'.json','r') as thefile:
                return json.load(thefile)
        except FileNotFoundError:
            raise FileNotFoundError("No such json file")
            sys.exit(1)

    def retrieve(self, json_stream, key):
        try:
            print(json_stream)
            return json_stream[key]
        except KeyError:
            raise KeyError(str(key) + " was not found")

    def gen_default_json(self):
        metadata = { "url":"http://10.147.4.69/compute/v2.1/servers",
                     "name": "cirros server" }
        server = self.gen_server_data()
        actual_data = {"server" : server}
        return { "actual_data" : actual_data, "metadata" : metadata }

    def gen_server_data(self):
        server_data = {"name" : "cirros server"}
        # GET IMAGES
        resp = json.loads(message(json_data={}, headers=self.headers,
                       url=config.IMAGES_URL).send_message("GET").text)
        server_data["imageRef"] = resp["images"][0]["id"]
        # GET FLAVORS
        resp = json.loads(message(json_data={}, headers=self.headers,
                       url=config.FLAVORS_URL).send_message("GET").text)
        server_data["flavorRef"] = resp["flavors"][9]["id"]
        # GET NETWORKS
        uid = {}
        resp = json.loads(message(json_data={}, headers=self.headers,
                       url=config.NETWORKS_URL).send_message("GET").text)
        for x in resp["networks"]:
            if x["name"] == 'private':
                uid["uuid"] = x["id"]
            elif x["name"] == 'public':
                self.public_access_ip = x["id"]


        server_data["networks"] = [uid]
        #server_data["accessIPv4"] = self.set_floating(uid["uuid"])
        return server_data

    def set_floating(self, the_id):
        #resp = json.loads(message(json_data={}, headers=self.headers,
        #               url=config.FLOATINGIP_POOL_URL).send_message("GET").text)
        #network_id = resp["floatingip_pools"][0]["network_id"]
        network_id = the_id
        respo = message(json_data=json.dumps({"floatingip": {
                            "floating_network_id" : network_id }}),
                             headers=self.headers,
                             url=config.FLOATINGIP_URL).send_message("POST")
        #return json.loads(respo.text)["floatingip"]["floating_ip_address"]
        with open('/home/thesis/net_elements/devstack_api/jsonfiles/default_ip.json',"w") as outfile:
            json.dump( json.loads(respo.text) , outfile, indent=4)
        return json.loads(respo.text)["floatingip"]["id"]
    # START OF FUNCTIONS FOR API CALL HANDLING

    def get_port_id(self, server_id):

        time.sleep(10)
        print(str(server_id))
        req = message( json_data=json.dumps({}),
                      url=config.SERVERS_URL+str(server_id)+"/os-interface",
                       headers={'Content-Type':'application/json',
                                'X-Auth-Token':self.auth_token} )
        resp = req.send_message('GET')
        print(resp.text)
        port_id = json.loads(resp.text)["interfaceAttachments"][0]["port_id"]
        return port_id

    def update_port_id(self, floating_id, port_id):
        payload = {"floatingip": {"port_id":port_id}}
        req = message( json_data=json.dumps(payload),
                      url=config.FLOATINGIP_URL+str(floating_id),
                       headers={'Content-Type':'application/json',
                                'X-Auth-Token':self.auth_token} )
        resp = req.send_message('PUT')


    # remote_activate_server -> just boots up the server with info specified at the server_type param (json file)
    def remote_activate_server(self, server_type='default'):
        if server_type == 'default':
            with open('/home/thesis/net_elements/devstack_api/jsonfiles/default.json',"w") as outfile:
                json.dump( self.gen_default_json(), outfile, indent=4)
        a = object_class.an_object(the_type=self.load_json_file(server_type))
        #print(json.dumps(a.dump_dict(), indent=4, sort_keys=True))
        req = message( json_data=json.dumps(a.dump_dict()),
                       url=a.url,
                       headers={'Content-Type':'application/json',
                                'X-Auth-Token':self.auth_token} )
        test = req.send_message('POST')
        print(test.text)
        print(a.name + ' server up!')

        print("ATTACHING PUBLIC FLOATING IP")
        public_floatingip_id = self.set_floating(self.public_access_ip)
        print("RETRIEVING PORT ID")
        port_id = self.get_port_id(json.loads(test.text)["server"]["id"])
        print("UPDATING PORT INFO")
        self.update_port_id(public_floatingip_id, port_id)



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
        r = requests.request(method,self.url,data=self.data,headers=self.headers)
        if not str(r.status_code).startswith("2"):
            print(self.headers)
            print(str(r.status_code) + " error")
            print(r.text)
            print(self.data)
            print(self.url)
            sys.exit(1)
        return r

