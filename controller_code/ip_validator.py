import socket
import multiprocessing as mp
import time
import sys

retvalue = None

def timeout(t, cmd, *args, **kwds):
    pool = mp.Pool(processes=1)
    result = pool.apply_async(cmd, args=args, kwds=kwds)
    try:
        retval = result.get(timeout=t)
    except mp.TimeoutError as err:
        pool.terminate()
        pool.join()
        raise
    else:
        return retval

def _ip_validator(ip_add):
    temp = socket.gethostbyname(ip_add)
    return temp

if __name__ == "__main__":
    ip_add = sys.argv[1]
    try:
        print(timeout(2, _ip_validator, ip_add))
    except mp.TimeoutError as err:
        print("False")
