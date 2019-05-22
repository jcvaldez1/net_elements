import sys
import requests
import json

class alias_object:
    def __init__(self, ip):
        # retrieve from localhost

        # now contains list of cache objects
        self.get_ip = ip
        self.aliased_ips = {}
        self.out_port = 2

    def update_alias(self):
        cache_list = json.loads(requests.get(self.get_ip + "alias/?format=json").text)
        for x in cache_list:
            #self.aliased_ips.append(x['address'])
            alias_id = str(x['alias'])
            alias_ip = json.loads(requests.get(self.get_ip + "service/" +
                                               alias_id + "/?format=json").text)
            if alias_ip["status"]:
                self.aliased_ips[x['address']] = (alias_ip['address'],alias_ip['server_id'])

    def dump_aliases(self):
        return self.aliased_ips # return in list form
