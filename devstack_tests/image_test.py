import sys
import time
from datetime import datetime
import urllib2
sys.path.insert(0, '/home/thesis/net_elements/devstack_api')
from main_handler_py2 import *

IMAGE_PATH =  "/home/thesis/images/streamz.qcow2"
IMAGES_URL='http://192.168.85.248/image/v2/images'
IMG_DOWNLOAD="https://s3-ap-southeast-1.amazonaws.com/ndsg/streamz.qcow2"
handler = main_handler()

def up_image_record():
    img_record = {"container_format":"bare", "disk_format":"qcow2",
                  "name":'streamz', "visibility":"public"}
    resp = requests.post(data=json.dumps(img_record),
                url=IMAGES_URL,
                headers=handler.headers)
    return resp
def image_up(resp):
    the_id = json.loads(resp.text)["id"]
    img_data = open(IMAGE_PATH, 'rb').read()
    custom_headers = handler.headers.copy()
    custom_headers["Content-Type"] = "application/octet-stream"
    re = requests.put(data=img_data,
                url=IMAGES_URL+"/"+the_id+"/file",
                headers=custom_headers )
    return the_id

def delete_image(the_id):
    requests.delete( url=IMAGES_URL+"/"+the_id,
                headers=handler.headers )

def download_image():
    file_x = urllib2.urlopen(IMG_DOWNLOAD)
    with open(IMAGE_PATH,'w') as f:
        while True:
            tmp = file_x.read(1024)
            if not tmp:
                break
            f.write(tmp)

def start():
    open("time_measurements.txt","w").close()
    the_file = open("time_measurements.txt","w")
    counter = 0
    while counter < 100:
        # ASSUME REQUESTS TO THE GLOBAL AND LOCAL
        # CONTROLLER ARE DONE FOR AND SHIET LMAOKAI

        # UP THE IMAGE
        the_file.write(str(datetime.utcnow())+", ")
        #print("DOWNLOADING IMAGE")
        download_image()
        # TIME HERE
        the_file.write(str(datetime.utcnow())+", ")
        #print("UPPING IMAGE")
        img_obj = up_image_record()
        # TIME HERE
        the_file.write(str(datetime.utcnow())+", ")
        #print("UPLOADING IMAGE")
        img_id = image_up(img_obj)
        # TIME HERE
        the_file.write(str(datetime.utcnow())+"\n")

        time.sleep(3)
        #print("DELETING IMAGE")
        delete_image(img_id)
        time.sleep(3)
        counter += 1

if __name__ == "__main__":
    start()
    pass

