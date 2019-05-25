import urllib2
url ="https://s3-ap-southeast-1.amazonaws.com/ndsg/Cache_noredirect.qcow2"
filepath="/home/thesis/images/blyat.qcow2"
file_x = urllib2.urlopen(url)
with open(filepath,'w') as f:
    while True:
        tmp = file_x.read(1024)
        if not tmp:
            break
        f.write(tmp)

