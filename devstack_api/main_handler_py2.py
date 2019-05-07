import socket
import requests
import json
import sys
import object_class
import config
import time
import ast
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
        self.private_network_id = None
        self.public_network_id = None

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

    def gen_default_json(self, server=None, metadata=None):
        if not metadata:
            metadata = { "url":"http://10.147.4.69/compute/v2.1/servers",
                         "name": "cirros server" }
        
        if not server:
            server = self.gen_server_data()
        
        actual_data = {"server" : server}
        return { "actual_data" : actual_data, "metadata" : metadata }

    def gen_server_data(self):
        server_data = {"name" : "cirros server"}
        # GET IMAGES
        # resp = json.loads(message(json_data={}, headers=self.headers,
        #                url=config.IMAGES_URL).send_message("GET").text)
        # server_data["imageRef"] = resp["images"][0]["id"]
        images = self.retrieve_images()
        server_data["imageRef"] = images[0]["id"]
        
        # GET FLAVORS
        # resp = json.loads(message(json_data={}, headers=self.headers,
        #                url=config.FLAVORS_URL).send_message("GET").text)
        # server_data["flavorRef"] = resp["flavors"][9]["id"]
        flavors = self.retrieve_flavors()
        server_data["flavorRef"] = flavors[9]["id"]
        # GET NETWORKS
        
        uid = {}
        uid["uuid"], self.public_access_ip = self.retrieve_network_ids()
        
        # resp = json.loads(message(json_data={}, headers=self.headers,
        #                url=config.NETWORKS_URL).send_message("GET").text)
        # for x in resp["networks"]:
        #     if x["name"] == 'private':
        #         uid["uuid"] = x["id"]
        #     elif x["name"] == 'public':
        #         self.public_access_ip = x["id"]


        server_data["networks"] = [uid]
        #server_data["accessIPv4"] = self.set_floating(uid["uuid"])
        return server_data

    # returns the private and public ids of the openstack network
    def retrieve_flavors(self):

        resp = json.loads(message(json_data={}, headers=self.headers,
                       url=config.FLAVORS_URL).send_message("GET").text)
        return resp["flavors"]

    def retrieve_images(self):
        
        resp = json.loads(message(json_data={}, headers=self.headers,
                       url=config.IMAGES_URL).send_message("GET").text)
        return resp["images"]

    def retrieve_network_ids(self):
        
        resp = json.loads(message(json_data={}, headers=self.headers, url=config.NETWORKS_URL).send_message("GET").text)
        for x in resp["networks"]:
            if x["name"] == 'private':
                private_id = x["id"]
            elif x["name"] == 'public':
                public_id = x["id"]
        return private_id, public_id

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
        return json.loads(respo.text)["floatingip"]
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
        public_floatingip_id = self.set_floating(self.public_access_ip)["id"]
        print("RETRIEVING PORT ID")
        port_id = self.get_port_id(json.loads(test.text)["server"]["id"])
        print("UPDATING PORT INFO")
        self.update_port_id(public_floatingip_id, port_id)
    
    def generate_server(self, imgref, flvref, srvname):
        server_data = {"name" : srvname, "imageRef" : imgref, "flavorRef" : flvref}
        server_data["networks"] = [ {"uuid" : self.private_network_id} ]
        return server_data
    
    def write_json(self, name, data):
        with open('/home/thesis/net_elements/devstack_api/jsonfiles/' + name + '.json',"w") as outfile:
                json.dump( data, outfile, indent=4)

    def server_stop_toggle(self, serv_name):
        stop_message = { "os-stop" : None}
        stopper = message( json_data=json.dumps(stop_message),
            url=config.SERVERS_URL+serv_name+"/action/",
            headers=self.headers ).send_message("POST")
    
    # Instantiates all of the images
    def remote_up_all(self):
        # retrieve network ids
        self.private_network_id, self.public_network_id = self.retrieve_network_ids()

        #retrive list of images and flavors
        images = self.retrieve_images()
        flavors = self.retrieve_flavors()

        # retrieve list of instances
        # instance sample:
        # { img_name, flavor_name, name, address , id }
        instances = ast.literal_eval(message( json_data=json.dumps({}),
            url=config.LOCAL_INSTANCES_URL,
            headers=self.headers ).send_message("GET").text)
        img_id = None
        flavor_id = None
        for inst in instances:
            print(inst)
            # retrieve img_id and flavor_id 
            img_id = self.find_object_match(inst["img_name"], "name", images)["id"]
            flavor_id = self.find_object_match(inst["flavor_name"], "name", flavors)["id"]
            inst_data = self.gen_default_json( self.generate_server( img_id,
                                                                    flavor_id,
                                                                    inst["name"] ), {} )
            self.write_json( inst["name"], inst_data )
            inst_object = object_class.an_object( the_type=self.load_json_file(
                inst["name"] ) )
            print(inst_object.dump_dict())
            resp = message(json_data=json.dumps( inst_object.dump_dict() ), url=config.SERVERS_URL, headers=self.headers).send_message('POST')
            print("HERE")
            server_id = json.loads(resp.text)["server"]["id"]
            floating_ip = self.set_floating( self.public_network_id )
            floating_ip_address = floating_ip["floating_ip_address"]
            floating_ip_id = floating_ip["id"]
            port_id = self.get_port_id( server_id )
            self.update_port_id( floating_ip_id, port_id )
            # UPDATE instance_ip PARAM
            inst["address"] = floating_ip_address
            message( json_data=json.dumps(inst),
                    url=config.LOCAL_INSTANCES_URL+inst.id,
                    headers=self.headers ).send_message("PUT")


        print "ALL INSTANCES UP"


    # finds object with val == object.attr for object in obj_list
    def find_object_match(self, val, attr, obj_list):
        for obj in obj_list:
            if obj[attr] == val:
                return obj
        else:
            return None   


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

