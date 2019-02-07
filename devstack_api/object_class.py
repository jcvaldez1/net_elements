import sys

#   CREATE A WRAPPER CLASS FOR THE IMAGE
#   IN ORDER FOR THE CREDENTIALS TO BE 
#   HANDLED EASIER

class an_object(object):
    def __init__(self, the_type):
        try:
            data_dict = the_type
            if isinstance(the_type, str): 
                try:
                    with open('./jsonfiles/'+the_type+'.json','r') as thefile:
                        data_dict = json.load(thefile)
                except FileNotFoundError:
                    raise FileNotFoundError("No such json file / remove the .json")
                    sys.exit(1)

            metadata = data_dict['metadata']
            print(">MEME")
            print(">Initializing " + metadata['name'] + " object")
            # you can like print extra metadata stuff here for utility
            self.__dict__ = metadata
            self.data = data_dict['actual_data']
        except FileNotFoundError:
            raise FileNotFoundError(the_type + ".json template does not exist! create one in ./jsonfiles/")
            sys.exit(1)

    def dump_dict(self):
        return self.data


