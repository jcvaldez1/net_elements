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

class SimpleMonitor13(learning_switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

        self.currently_banned_ips = []
        self.mac_patch_url = "https://cs198globalcontroller.herokuapp.com/devices/"

        self.global_header = {'User-Agent' : 'DepEd-1' }
        # MACH CHECKER NFV VARS
        self.mac_addresses = {}
        self.mac_addresses_current = {}
        self.registered_macs_url = 'https://cs198globalcontroller.herokuapp.com/locals/1'
        self.registered_macs_local_url = 'http://localhost:8000/firewall/devices/1/?format=json'
        self.mac_checker_thread = hub.spawn(self._mac_checker)

        # IP BLOCKER NFV VARS
        self.banned_ips = []
        self.banned_ip_url = 'https://cs198globalcontroller.herokuapp.com/lists/1'
        self.banned_ip_local_url = "http://localhost:8000/firewall/blacklist/1/?format=json"
        self.banned_ip_checker_thread = hub.spawn(self._ip_checker)

        # CURRENTLY BANNED IPs AS TO NOT UNNECESSARILY RE-ADD ALREADY EXISTING FLOWS

        # This section is for the NFV aliasing
        self.ALIAS_OBJECT_IP = "http://localhost:8000/cache/"


        self.alias_url = "http://localhost:8000/cache/alias/?format=json"
        self.alias_checker_thread = hub.spawn(self._alias_checker)
        self.alias_list = {}
        self.accessip = ""

        # TEMPORARY CONSTANTS
        self.NFV_MAC = constants.NFV_MACHINE_MAC
        self.SELF_IP = "10.147.4.58"
        self.INTERNET_PORT = 5


    def _alias_checker(self):
        while True:
            self.aliaser = aliaser.alias_object(self.ALIAS_OBJECT_IP)
            self.aliaser.update_alias()
            for alias, val in self.aliaser.dump_aliases().iteritems():

                connection_health = self.live_connection(alias)
                if not alias in self.alias_list:
                    self.alias_list[alias] = True
                if (not connection_health) and (self.alias_list[alias]):
                    self.alias_list[alias] = False
                    exit_code = call("python3 /home/thesis/net_elements/devstack_api/image_boot.py --server default --user user_basic", shell=True)
                    self.accessip = self.update_ip("default_ip")

                elif (connection_health) and (not self.alias_list[alias]):
                    # DELETE THE INSTANCE PLEB KAPPA
                    pass
                if (not connection_health) and ( not self.alias_list[alias]):
                    for dp in self.datapaths.values():
                        ofproto = dp.ofproto
                        parser = dp.ofproto_parser
                        actions = [ parser.OFPActionSetField(ipv4_dst=self.accessip) ,parser.OFPActionSetField(eth_dst=self.NFV_MAC) , parser.OFPActionOutput(self.aliaser.out_port) ]
                        super(SimpleMonitor13, self).add_flow(dp, 10, parser.OFPMatch(eth_type=0x0800, ipv4_dst=self._validate_ip(alias) ), actions)
                        #INGOING
                        actions = [ parser.OFPActionSetField(ipv4_src=alias)
                                   ,parser.OFPActionOutput(4) ]
                        super(SimpleMonitor13, self).add_flow(dp, 10, parser.OFPMatch(eth_type=0x0800, ipv4_src=self.accessip ), actions)

            hub.sleep(8)

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

    def live_connection(self, hostname):
        try:
            stringy = ""
            if (not hostname.startswith("http://")) or (not hostname.startswith("https://")):
                stringy = "http://"
            urllib2.urlopen(stringy + hostname, timeout=2)
            return True
        except urllib2.URLError as err: 
            return False

    def _validate_ip(error, ip_add):
        print(ip_add)
        ip = None
        try:
            socket.inet_aton(ip_add)
            ip = ip_add
        except socket.error:
            temp = socket.gethostbyname(ip_add)
            ip = temp.split(".")[0] + "." + temp.split(".")[1] + ".0.0/16"

        return ip

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
                           key=lambda flow: (flow.match['ipv4_dst'])):
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
