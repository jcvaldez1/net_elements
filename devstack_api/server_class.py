import sys

#   CREATE A WRAPPER CLASS FOR THE IMAGE
#   IN ORDER FOR THE CREDENTIALS TO BE 
#   HANDLED EASIER

class an_object(object):
    def __init__(self, the_type):
        try:
            metadata = 
            actual_data = json.load(json_file)['actual_data']
            print(">MEME")
            print(">Initializing " + metadata['name'] + " object")
            # you can like print extra metadata stuff here for utility
            self.__dict__ = json.load(json_file)['metadata']
            self.data = json.load(json_file)['actual_data']
        except FileNotFoundError:
            raise FileNotFoundError(the_type + " template does not exist! create one in ./jsonfiles/")
            sys.exit(1)

    def dict_dump(self):
        return self.data


