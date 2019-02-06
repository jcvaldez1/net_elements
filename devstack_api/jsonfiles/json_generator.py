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

with open('access_token_json.json',"w") as outfile:
    json.dump( {"auth":auth } , outfile, indent=4)
