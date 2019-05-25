import sys
from datetime import datetime




def print_shit(filename):
    counter = 0
    download_time = 0
    container_time = 0
    up_time = 0
    the_file = open(filename, "r")
    open("download_measures.txt","w").close()
    open("container_measures.txt","w").close()
    open("up_measures.txt","w").close()
    download = open("download_measures.txt","w")
    container = open("container_measures.txt","w")
    up = open("up_measures.txt","w")
    for line in the_file:
        the_list = line.strip("\n").split(", ")
        time_list = [ datetime.strptime( x, "%Y-%m-%d %H:%M:%S.%f") for x in the_list ]
        counter += 1
        download_add = (time_list[1] - time_list[0]).total_seconds()
        container_add = (time_list[2] - time_list[1]).total_seconds()
        up_add = (time_list[3] - time_list[2]).total_seconds()
        download.write(str(download_add)+",")
        container.write(str(container_add)+",")
        up.write(str(up_add)+",")
        download_time += download_add
        container_time += container_add
        up_time += up_add

    counter *= 1.0
    download_time = download_time/counter
    container_time = container_time/counter
    up_time = up_time/counter
    print("tests: " + str(counter))
    print("average download time: " + str(download_time))
    print("average container time: " + str(container_time))
    print("average up time: " + str(up_time))
    the_file.close()
    download.close()
    container.close()
    up.close()


if __name__ == "__main__":
    print_shit(sys.argv[1])
