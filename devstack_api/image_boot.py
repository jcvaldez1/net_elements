import main_handler
import server_object
import argparse, sys

class booter():
    
    def __init__(self, args):
        self.args = args
    
    def boot_up(self):
        theuser= main_handler(user_object=self.args.user)
        theuser.remote_activate(server_type=self.args.server)



if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--user', help='user json object name')
    parser.add_argument('--server', help='server json object name')
    args=parser.parse_args()
    a = booter(args)
    a.boot_up()
