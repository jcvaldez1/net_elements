
# PUT YOUR JSON TEMPLATES HERE
Dump all JSON templates to be used in your API scripts here <br/>
Check the "object_class.py" wrapper for the serialization implementation <br/>

### Contents:
1.) "metadata" -> put all the data (name, url, timestamp, etc.) that you need to access but does not need to be in the actual payload in here.<br/>
2.) "actual_data" -> put all the necessary payload data here.
> Refer to the basic templates (user_basic.json, server_basic.json) for more info
* user_basic -> basic user json payload template for retrieving access tokens <br/>
* server_basic -> basic server json payload template for remote activating a server<br/>
###### When creating new json templates ( e.g. "test.json" ), you can use them as params for the API function scripts ( e.g. "python3 image_boot.py --user=test" without the ".json" file extension
 
