# AUTH TOKEN DEETS
NFV_IP = '192.168.85.248'
AUTH_TOKEN_KEY='X-Subject-Token'
FLAVORS_URL='http://'+NFV_IP+'/compute/v2.1/flavors'
IMAGES_CREATE_URL='http://'+NFV_IP+'/image/v2/images'
IMAGES_URL='http://'+NFV_IP+'/image/v2/images'
#IMAGES_URL='http://'+NFV_IP+'/compute/v2.1/images'
#NETWORKS_URL='http://'+NFV_IP+'/compute/v2.0/networks'
NETWORKS_URL = 'http://'+NFV_IP+':9696/v2.0/networks'
FLOATINGIP_POOL_URL='http://'+NFV_IP+':9696/v2.0/floatingip_pools/'
FLOATINGIP_URL='http://'+NFV_IP+':9696/v2.0/floatingips/'
SERVERS_URL='http://'+NFV_IP+'/compute/v2.1/servers/'
LOCAL_INSTANCES_URL='http://127.0.0.1:8000/cache/service/'
RESOURCE_URL="http://"+NFV_IP+"/metric/v1/resource/instance/"
METRIC_URL="http://"+NFV_IP+"/metric/v1/metric/"
CPU_UTIL_TIME_START=5
