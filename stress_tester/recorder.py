from urllib.request import urlopen
import sys

link_to_movie = sys.argv[2]
file_name = './vids/'+ sys.argv[1] + '.mp4' 
response = urlopen(link_to_movie)
with open(file_name,'wb') as f:
    f.write(response.read())
