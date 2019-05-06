import urllib2

def internet_on():
    try:
        urllib2.urlopen('8ch.net', timeout=2)
        return True
    except urllib2.URLError as err: 
        return False

print(internet_on())
