import json
import requests
import time
from datetime import datetime

the_file = open("local_times.txt","w")
for i in range(0,100):

    print("TEST NUMBER: "+ str(i))
    the_file.write(str(datetime.utcnow())+", ")
    URL = "http://localhost:8000/cache/service/"
    data={"name":"name", "img_name": "img_name" ,
          "flavor_name": "flavor_name" , "address":"0.0.0.0",
          "server_id":"None", "live":False}
    resp = requests.post(URL,data=json.dumps(data),
                  headers={"Content-Type":"application/json"})
    the_file.write(str(datetime.utcnow())+"\n")
    the_dict = json.loads(resp.text)
    the_id = the_dict["id"]
    new_url = URL + str(the_id) + "/"
    requests.delete(new_url)
the_file.close()
