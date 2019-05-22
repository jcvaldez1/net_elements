# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from operator import attrgetter 
#from ryu.app import meter_poller
#import meter_poller
import learning_switch
import os
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub


# IMPORT NEVESSARY LIBRARIES FOR THE NFVs
import socket
import requests
import constants
import json
from datetime import datetime
import aliaser
import os
from subprocess import call
import ast
import urllib2
from ryu.cfg import CONF
import sys
import subprocess
sys.path.insert(0, '/home/thesis/net_elements/devstack_api')
from main_handler_py2 import *


class SimpleMonitor13(learning_switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        #with open("./test.json" , "w") as outfile:
        #    json.dumps(CONF.__dict__, outfile, indent=4)
        #print(CONF.controller_mode)

        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}

        self.currently_banned_ips = []
        self.mac_patch_url = "https://cs198globalcontroller.herokuapp.com/devices/"

        self.global_header = {'User-Agent' : 'DepEd-1' }
        # MACH CHECKER NFV VARS
        self.mac_addresses = {}
        self.mac_addresses_current = {}
        self.registered_macs_url = 'https://cs198globalcontroller.herokuapp.com/locals/1'
        self.registered_macs_local_url = 'http://localhost:8000/firewall/devices/1/?format=json'

        # IP BLOCKER NFV VARS
        self.banned_ips = []
        self.banned_ip_url = 'https://cs198globalcontroller.herokuapp.com/lists/1'
        self.banned_ip_local_url = "http://localhost:8000/firewall/blacklist/1/?format=json"

        # CURRENTLY BANNED IPs AS TO NOT UNNECESSARILY RE-ADD ALREADY EXISTING FLOWS

        # This section is for the NFV aliasing
        self.ALIAS_OBJECT_IP = "http://localhost:8000/cache/"


        self.images_url = "http://cs198globalcontroller.herokuapp.com/images/?format=json"
        self.images_local_url = "http://localhost:8000/cache/service/"

        self.alias_url = "http://localhost:8000/cache/alias/?format=json"
        self.alias_list = {}
        self.accessip = ""
        self.queued_images = []

        # TEMPORARY CONSTANTS
        self.NFV_MAC = constants.NFV_MACHINE_MAC
        self.SELF_IP = "10.147.4.58"
        self.INTERNET_PORT = 5
        self.CLIENT_SWITCH_PORT = 4
        #self.alias_handler = main_handler()
        self.HOSTNAME_IPS = {}
        self.IP_STATUS = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.alias_handler = main_handler()
        self.image_upper = hub.spawn(self._image_upper)

        # START THE ALIASES
        if CONF.controller_mode == 'cold':
            print("\n\n\nINITIALIZING COLD MODE BABYYYYYY")
            self.aliaser_thread = hub.spawn(self._aliaser_coldmode)
            pass

        elif CONF.controller_mode == 'hot':
            self.alias_handler.remote_up_all()
            self.aliaser_thread = hub.spawn(self._aliaser_hotmode)
            pass

        elif CONF.controller_mode == 'hot_test':
            self.alias_handler.remote_up_all()
            self.aliaser_thread = hub.spawn(self._aliaser_hot_test)
            pass

        elif CONF.controller_mode == 'cold_test':
            self.aliaser_thread = hub.spawn(self._aliaser_cold_test)
            pass

        else:
            #hub.spawn(self._test_thread,6,9)
            print("NO CONTROLLER MODE AVAILABLE")

        #self.mac_checker_thread = hub.spawn(self._mac_checker)
        #self.banned_ip_checker_thread = hub.spawn(self._ip_checker)
        #self.alias_checker_thread = hub.spawn(self._alias_checker)

    def _image_upper(self):
        while True:
            damn = json.loads(requests.get(self.images_url, headers=self.global_header).text)
            temp = json.loads(requests.get(self.images_local_url+"?format=json").text)
            img_local = [ x["img_name"] for x in temp ]
            for x in damn:
                # ASSUMED THAT IF NOT IN LOCAL DATABASE, 
                # THEN A LOCAL COPY IS NOT PRESENT
                local_img = self.find_object_match()
                update_time = datetime.strptime(x["updated_at"],'%Y-%m-%dT%H:%M:%S.%fZ')
                version_time = datetime.now()
                if not x["img_name"] in img_local:
                    print("\n\n\n"+str(x)+"\n\n\n")
                    data={"name":x["name"], "img_name":x["img_name"],
                          "flavor_name":x["flavor_name"], "address":"0.0.0.0",
                          "server_id":"None", "live":False}
                    resp = requests.post(self.images_local_url,data=json.dumps(data),
                                  headers={"Content-Type":"application/json"})
                    # THREAD THE FUNCTION FOR DOWNLOADING 
                    # FOR IT MAY TAKE A WHILE
                    hub.spawn(self._image_setup, x, resp)
                elif (x["img_name"] in img_local) and (update_time > version_time):
                    pass
            hub.sleep(10)


    # finds object with val == object.attr for object in obj_list
    def find_object_match(self, val, attr, obj_list):
        for obj in obj_list:
            if obj[attr] == val:
                return obj
        else:
            return None

    def _image_setup(self, image_object, resp):
        # DOWNLOAD IMAGE OMEGALUL

        print("\n\n\nDOWNLOADING IMAGE\n\n\n")
        temp = urllib2.urlopen(image_object["link"])
        filedata = temp.read()
        path = '/home/thesis/images/'+image_object["img_name"]+'.qcow2'
        with open(path, 'wb') as f:
            f.write(filedata)

        self.alias_handler.up_image(image_object, path)
        print("\n\n\nPOSTING DATA\n\n\n")
        # POST DATA OMEGALUL
        the_object = json.loads(resp.text)
        the_object["status"] = True
        the_id = the_object.pop('id', None)
        resp = requests.put(self.images_local_url+str(the_id)+"/",data=json.dumps(the_object),
                      headers={"Content-Type":"application/json"})
        # IF HOTMODE UP IMMEDIATELY
        if CONF.controller_mode == 'hot':
            instance = json.loads(resp.text)
            # UP THE INSTANCE
            self.alias_handler.remote_up_server([instance])

    def _aliaser_cold_test(self):
        counter = 0
        connection_health = True
        while True:
            self.aliaser = aliaser.alias_object(self.ALIAS_OBJECT_IP)
            self.aliaser.update_alias()
            if counter == 10:
                counter = 0
                connection_health = not connection_health
            for alias, val in self.aliaser.dump_aliases().iteritems():
                #hub.spawn(self._cold_aliaser_thread, alias, val)
                alias_status = self.nfv_status_check(val[1])
                nfv_ip=self._validate_ip(val[0])
                real_ip=self._validate_ip(alias)
                #connection_health = self.live_connection(alias)
                if not alias_status == "BUSY" :
                    # CONNECTION DOWN AND INSTANCE DOWN
                    if ( not connection_health ) and ( not alias_status ):
                        # UP THE INSTANCE
                        print("\n\n\n\nCONNECTION DOWN INSTANCE DOWN\n\n\n")
                        if alias_status == None:
                            # GET INSTANCE OBJECT USING SERVER ID
                            instance = json.loads(requests.get(self.ALIAS_OBJECT_IP+"service/" + "?server_id=" + val[1]+"&format=json").text)
                            # UP THE INSTANCE
                            self.alias_handler.remote_up_server(instance)
                            pass
                        else:
                            self.alias_handler.server_stop_toggle(val[1],"start")
                        alias_status = True

                    # CONNECTION UP AND INSTANCE UP
                    if (connection_health) and ( alias_status ):
                        # STOP THE INSTANCE
                        print("\n\n\n\nCONNECTION UP INSTANCE UP\n\n\n")
                        self.alias_handler.server_stop_toggle(val[1],"stop")
                        alias_status = False
                        pass
                    # CONNECTION DOWN AND INSTANCE UP
                    elif ( not connection_health ) and ( alias_status ):
                        print("\n\n\n\nCONNECTION DOWN INSTANCE UP\n\n\n")

                        for dp in self.datapaths.values():
                            print("\n\n\n"+str(val)+"\n\n\n")
                            ofproto = dp.ofproto
                            parser = dp.ofproto_parser
                            act_set = parser.OFPActionSetField
                            act_out = parser.OFPActionOutput
                            # OUTGOING 
                            actions = [ act_set(ipv4_dst=nfv_ip),
                                       act_set(eth_dst=self.NFV_MAC), act_out(self.aliaser.out_port) ]
                            match = parser.OFPMatch(eth_type=0x0800, ipv4_dst=real_ip)
                            super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                            # INGOING
                            actions = [
                                act_set(ipv4_src=real_ip), act_out(self.CLIENT_SWITCH_PORT) ]
                            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=nfv_ip)
                            super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                            print("\n\n\nEXEMPT CONTROLLER\n\n\n")
                            actions = [ parser.OFPActionOutput(constants.INTERNET_SWITCH_PORT) ]
                            match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=real_ip,eth_src=constants.CONTROLLER_ETH)
                            super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

                            actions = [ parser.OFPActionOutput(constants.CONTROLLER_SWITCH_PORT) ]
                            match = parser.OFPMatch(eth_type=0x0800,ipv4_src=real_ip,eth_dst=constants.CONTROLLER_ETH)
                            super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)
                    # FOR CONNECTION UP INSTANCE DOWN 
                    # DO NOTHING BUT THE NORMAL ROUTINE

            counter += 1
            hub.sleep(10)

    def _aliaser_hot_test(self):
        open("detection_timestamps.txt", "w").close()
        last_flag = None
        while True:
            self.aliaser = aliaser.alias_object(self.ALIAS_OBJECT_IP)
            self.aliaser.update_alias()
            # GO FOR 10 LOOPS BEFORE SWITCHING MODES
            for key, val in self.aliaser.dump_aliases().iteritems():
                print("\n\n\n" + str(key) + str(val))
                # VAL = ( NFV_IP , SERVER_ID )
                nfv_ip=self._validate_ip(val[0])
                real_ip=self._validate_ip(key)
                connection_health = self.live_connection(key)

                if last_flag == None:
                    last_flag = connection_health

                if last_flag != connection_health:
                    a = open("detection_timestamps.txt", "a+")
                    a.write(str(datetime.now().time())+"\n")
                    a.close()

                if not connection_health:
                    for dp in self.datapaths.values():
                        print("\n\n\n"+str(val)+"\n\n\n")
                        ofproto = dp.ofproto
                        parser = dp.ofproto_parser
                        act_set = parser.OFPActionSetField
                        act_out = parser.OFPActionOutput
                        # OUTGOING 
                        actions = [ act_set(ipv4_dst=nfv_ip),
                                   act_set(eth_dst=self.NFV_MAC), act_out(self.aliaser.out_port) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_dst=real_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        # INGOING
                        actions = [
                            act_set(ipv4_src=real_ip), act_out(self.CLIENT_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=nfv_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        print("\n\n\nEXEMPT CONTROLLER\n\n\n")
                        actions = [ parser.OFPActionOutput(constants.INTERNET_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=real_ip,eth_src=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

                        actions = [ parser.OFPActionOutput(constants.CONTROLLER_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_src=real_ip,eth_dst=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

                last_flag = connection_health

            hub.sleep(5)

    def _aliaser_hotmode(self):
        while True:
            self.aliaser = aliaser.alias_object(self.ALIAS_OBJECT_IP)
            self.aliaser.update_alias()
            for key, val in self.aliaser.dump_aliases().iteritems():
                # VAL = ( NFV_IP , SERVER_ID )
                #hub.spawn(self._alias_determiner_hot(alias, val))

                #print("\n\n\n" + str(alias) + "\n\n\n")
                nfv_ip=self._validate_ip(val[0])
                real_ip=self._validate_ip(key)
                connection_health = self.live_connection(key)
                print("\n\n\n"+str(connection_health)+"\n\n\n")
                if (not connection_health):
                    for dp in self.datapaths.values():
                        print("\n\n\n"+str(val)+"\n\n\n")
                        ofproto = dp.ofproto
                        parser = dp.ofproto_parser
                        act_set = parser.OFPActionSetField
                        act_out = parser.OFPActionOutput
                        # OUTGOING 
                        actions = [ act_set(ipv4_dst=nfv_ip),
                                   act_set(eth_dst=self.NFV_MAC), act_out(self.aliaser.out_port) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_dst=real_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        # INGOING
                        actions = [
                            act_set(ipv4_src=real_ip), act_out(self.CLIENT_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=nfv_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        print("\n\n\nEXEMPT CONTROLLER\n\n\n")
                        actions = [ parser.OFPActionOutput(constants.INTERNET_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=real_ip,eth_src=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

                        actions = [ parser.OFPActionOutput(constants.CONTROLLER_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_src=real_ip,eth_dst=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

            hub.sleep(10)

    def _test_thread(self, a, b):
        print("\n\n\n"+str(a+b) + "\n\n\n")
    def _aliaser_coldmode(self):
        while True:
            self.aliaser = aliaser.alias_object(self.ALIAS_OBJECT_IP)
            self.aliaser.update_alias()
            print("\n\n\nWHAT\n\n\n")
            for alias, val in self.aliaser.dump_aliases().iteritems():
                hub.spawn(self._cold_aliaser_thread, alias, val)
                alias_status = self.nfv_status_check(val[1])
                nfv_ip=self._validate_ip(val[0])
                real_ip=self._validate_ip(alias)
                connection_health = self.live_connection(alias)
                # CONNECTION DOWN AND INSTANCE DOWN
                if ( not connection_health ) and ( not alias_status ) and ( not alias_status=="nothing" ):
                    # UP THE INSTANCE
                    print("\n\n\n\nCONNECTION DOWN INSTANCE DOWN\n\n\n")
                    if alias_status == None:
                        # GET INSTANCE OBJECT USING SERVER ID
                        instance = json.loads(requests.get(self.ALIAS_OBJECT_IP+"service/" + "?server_id=" + val[1]+"&format=json").text)
                        # UP THE INSTANCE
                        self.alias_handler.remote_up_server(instance)
                        pass
                    else:
                        self.alias_handler.server_stop_toggle(val[1],"start")
                    alias_status = True

                # CONNECTION UP AND INSTANCE UP
                if (connection_health) and ( alias_status ) and ( not alias_status == "nothing"):
                    # STOP THE INSTANCE
                    print("\n\n\n\nCONNECTION UP INSTANCE UP\n\n\n")
                    self.alias_handler.server_stop_toggle(val[1],"stop")
                    alias_status = False
                    pass
                # CONNECTION DOWN AND INSTANCE UP
                elif ( not connection_health ) and ( alias_status ) and ( not alias_status == "nothing"):
                    print("\n\n\n\nCONNECTION DOWN INSTANCE UP\n\n\n")

                    for dp in self.datapaths.values():
                        print("\n\n\n"+str(val)+"\n\n\n")
                        ofproto = dp.ofproto
                        parser = dp.ofproto_parser
                        act_set = parser.OFPActionSetField
                        act_out = parser.OFPActionOutput
                        # OUTGOING 
                        actions = [ act_set(ipv4_dst=nfv_ip),
                                   act_set(eth_dst=self.NFV_MAC), act_out(self.aliaser.out_port) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_dst=real_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        # INGOING
                        actions = [
                            act_set(ipv4_src=real_ip), act_out(self.CLIENT_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=nfv_ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, match, actions)

                        print("\n\n\nEXEMPT CONTROLLER\n\n\n")
                        actions = [ parser.OFPActionOutput(constants.INTERNET_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=real_ip,eth_src=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)

                        actions = [ parser.OFPActionOutput(constants.CONTROLLER_SWITCH_PORT) ]
                        match = parser.OFPMatch(eth_type=0x0800,ipv4_src=real_ip,eth_dst=constants.CONTROLLER_ETH)
                        super(SimpleMonitor13, self).add_flow(dp, 15, match, actions, None,True)
                # FOR CONNECTION UP INSTANCE DOWN 
                # DO NOTHING BUT THE NORMAL ROUTINE

            hub.sleep(10)

    def _cold_aliaser_thread(self, alias, val ):
        pass

    def live_connection(self,hostname):

        def bool_parse(string):
            if string == "True":
                return True
            elif string == "False":
                return False
            else:
                return None
        #print("\n\n\nSTARTING POLLER\n\n\n")
        url = hostname
        proc = subprocess.Popen(['python','/home/thesis/net_elements/controller_timestamps/connection_tester.py',  url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stringer = proc.communicate()[0][:-1]
        exit_code = proc.wait()
        #print("\n\n\nENDING POLLER"+ str(stringer)+ "\n\n\n")
        return bool_parse(stringer)

    def nfv_status_check(self, server_id):
        # RETURNS NONE IF THE SERVER DOES NOT EXIST
        return self.alias_handler.server_status(server_id)

    def update_ip(self, server_type):
        try:
            with open('/home/thesis/net_elements/devstack_api/jsonfiles/'+server_type+'.json','r') as thefile:
                data_dict = json.load(thefile)
        except FileNotFoundError:
            raise FileNotFoundError("No such json file / remove the .json")
            sys.exit(1)
        headers = {"Content-Type":"application/json"}

        the_id = self.id_retrieval(self.ALIAS_OBJECT_IP+"service/?format=json&name=video_cache", headers)
        new_ip = data_dict["floatingip"]["floating_ip_address"]
        requests.request("PUT", self.ALIAS_OBJECT_IP+'service/'+str(the_id), data=json.dumps({"address":new_ip}), headers=headers)
        return new_ip

    def id_retrieval(self, url, headers):
        resp = requests.get(url, headers=headers)
        print(resp)
        return json.loads(resp.text)[0]["id"]

    def _validate_ip(self, ip_add, status=True):

        def bool_parse(string):
            if (string == "False") or (string == "None"):
                return False
            else:
                return string
        #print("\n\n\nSTARTING VALIDATOR\n\n\n")
        url = ip_add

        proc = subprocess.Popen(['python','/home/thesis/net_elements/controller_code/ip_validator.py',  url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stringer = proc.communicate()[0][:-1]
        exit_code = proc.wait()
        #print("\n\n\nENDING VALIDATOR"+ str(stringer)+ "\n\n\n")
        the_val = bool_parse(stringer)
        if not the_val:
            try:
                the_val = self.IP_STATUS[ip_add]
            except:
                print("NO IP AVAILABLE FOR "+ip_add)
                sys.exit(1)

        self.IP_STATUS[ip_add] = the_val
        return the_val

    def _ip_checker(self):
        while True:
            damn = json.loads(requests.get(self.banned_ip_url, headers=self.global_header).text)["websites"]
            banned_global = [ x["ip_address"] for x in damn ]
            temp = json.loads(requests.get(self.banned_ip_local_url).text)["address"]
            banned_local = ast.literal_eval(temp)
            banned_ips = banned_local + list(set(banned_global) - set(banned_local))
            print(banned_ips)
            for ip in banned_ips:
                #if not ip in self.currently_banned_ips:
                    # ACCESS ALL DATAPATHS
                    for dp in self.datapaths.values():
                        # ADD FLOW HERE
                        ofproto = dp.ofproto
                        parser = dp.ofproto_parser
                        #print(ip)
                        super(SimpleMonitor13, self).add_flow(dp, 10, 
                        parser.OFPMatch(eth_type=0x0800, ipv4_dst=self._validate_ip(ip) ), [])
            hub.sleep(10)

    def _mac_checker(self):
        while True:
            # RETRIEVE REGISTERED MAC LIST
            damn = json.loads(requests.get(self.registered_macs_url, headers=self.global_header).text)["devices"]
            reg_global = [ x["identifier"] for x in damn ]

            counter = {}
            number = 0
            for x in reg_global:
                counter[x] = damn[number]['id']
                number = number + 1

            temp = json.loads(requests.get(self.registered_macs_local_url).text)["macs"]
            reg_local = ast.literal_eval(temp)
            self.mac_addresses = reg_local + list(set(reg_global) - set(reg_local))

            #self.mac_addresses = dict(self.mac_addresses_current)
            for mac in self.mac_addresses:
                  # check time differene
                  # print(mac)
                  # print((datetime.utcnow() -  self.mac_addresses[mac]).total_seconds())
                  the_header = {'User-Agent' : 'DepEd-1', 'Content-Type':'application/json'}
                  if not mac in self.mac_addresses_current:
                       self.mac_addresses_current[mac] = datetime.utcnow()
                  else:
                      if (datetime.utcnow() -  self.mac_addresses_current[mac]).total_seconds() > 20:
                           payload = { "device": { "status" : "Dead" } }
                           print("RED ALERT " + mac + " IS MISSING")
                      else:
                           payload = { "device": { "status" : "Alive" } }
                      if mac in counter:
                           requests.patch(self.mac_patch_url + str(counter[mac]) + "/", json.dumps(payload),
                           headers=the_header)
                  
            hub.sleep(10)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            self.currently_banned_ips = []
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(8)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            self.logger.info(stat)
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

            # UPDATE TIMESTAMPS ON MAC CHECKERS
            self.mac_addresses_current[stat.match['eth_dst']] = datetime.utcnow()
            # UPDATE CURRENTLY BANNED IP ADDRESSES
        # REMOVED PRIORITY == 1 CONSTRAINT
        # THIS IS FOR THE IPs
        for stat in sorted([flow for flow in body if flow.priority == 10],
                           key=lambda flow: (flow.match['ipv4_dst'] if
                                             'ipv4_dst' in flow.match else None)):
            try:
                if(not stat.match['ipv4_dst'] in self.currently_banned_ips):
                    self.currently_banned_ips.append(stat.match['ipv4_dst'])
            except:
                pass

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
