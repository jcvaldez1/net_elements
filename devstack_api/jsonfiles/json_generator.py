import json

# FOR ACCESS TOKEN
auth = dict()
identity = dict()
password = dict()
user = dict()
domain=dict()
project=dict()

user['name'] = "admin"
user['domain'] = { "name":"Default" }
user['password'] = "ndsg123"
identity['methods'] = ["password"]
identity['password']=user

project['domain']= { "id":"default" }
project['name']="admin"

auth['identity']=identity
auth['scope']={ "project":project }

actual_data={"auth":auth}
metadata={"name":"basic user", "url":"localhost:8000/something/users"}

with open('user_basic.json',"w") as outfile:
    json.dump( {"actual_data":actual_data, "metadata":metadata} , outfile, indent=4)


server = {"name":"test", "imageRef":"012983as-adsff23f23", "flavorRef":1}

actual_data={"server":server}
metadata={"name":"basic server", "url":"localhost:8000/compute/v2.1/servers"}

with open('server_basic.json',"w") as outfile:
    json.dump( {"actual_data":actual_data, "metadata":metadata} , outfile, indent=4)
