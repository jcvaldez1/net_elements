import subprocess
url = "www.8ch.net"
while True:
    #exit_code = subprocess.call("python /home/thesis/net_elements/controller_code/connection_tester.py " + url, shell=True)


    proc = subprocess.Popen(['python','/home/thesis/net_elements/controller_code/connection_tester.py',  url], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.communicate()[0][:-1])
    exit_code = proc.wait()
    #print(exit_code)
    #a = subprocess.call('python /home/thesis/net_elements/controller_code/connection_tester.py ' +url)
