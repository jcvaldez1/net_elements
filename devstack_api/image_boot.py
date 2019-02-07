import main_handler
import object_class
import argparse, sys

class booter():
    
    def __init__(self, arguments):
        self.arguments = arguments
    
    def boot_up(self):
        theuser= main_handler.main_handler(user_object=self.arguments.user)
        theuser.remote_activate_server(server_type=self.arguments.server)



if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--user', help='user json object name', default='user_basic')
    parser.add_argument('--server', help='server json object name', default='server_basic')
    args=parser.parse_args()
    a = booter(args)
    a.boot_up()
