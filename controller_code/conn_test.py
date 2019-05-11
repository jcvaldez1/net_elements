from multiprocessing import *
import time
from requests import *

def do_actions(url, valboy):
    headers = {
            'User-Agent': 'My User Agent 1.0',
            'From': 'youremail@domain.com'  # This is another valid field
    }
    a = get(url, headers=headers).status_code
    print(a)
    valboy[url] =  a

if __name__ == '__main__':
    while True:
        vale = Manager()
        valboy = vale.dict()
        valboy["http://www.deped.gov.ph"] = None
        action_process = Process(target=do_actions,
                                 args=("http://www.deped.gov.ph", valboy))
        action_process.start()
        action_process.join(timeout=2)
        action_process.terminate()
        print(valboy)
