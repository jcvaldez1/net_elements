import sys
from datetime import datetime

def shitlord(filename):
    counter = 0
    the_file = open(filename, "r")
    local_time = 0
    open("local_measures.txt","w").close()
    local = open("local_measures.txt","w")
    for line in the_file:
        the_list = line.strip("\n").split(", ")
        time_list = [ datetime.strptime( x, "%Y-%m-%d %H:%M:%S.%f") for x in the_list ]
        counter += 1
        local_add = (time_list[1] - time_list[0]).total_seconds()
        local.write(str(local_add)+",")
        local_time += local_add

    counter *= 1.0
    local_time = local_time/counter
    print("tests: " + str(counter))
    print("average local time: " + str(local_time))
    local.close()

if __name__=="__main__":
    shitlord(sys.argv[1])
