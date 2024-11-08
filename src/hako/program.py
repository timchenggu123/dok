from hako.db import Database 
from hako.interface import *

class StateMachine():
    def __init__(self):
        '''
        This is the main statemachine of the program.
        responsible for state persistence across runs
        '''
        self.db = Database()
    
    def create_hako(self, args):
        name = args.name
        if self.db.select_hako(name):
            raise NameError(f"Hako named '{name}' already exists")
        if args.image:
            self.create_hako_from_image(args) 
            return
        raise ValueError("Please specify an image.")
    
    def create_hako_from_image(self, args):
        image = args.image
        name  = args.name
        docker_args = args.args
        docker_command = "sleep infinity"
        docker_create_container(name, image, docker_args, docker_command)
        self.db.insert_hako(name, image, docker_args, docker_command) 

    def remove_hako(self,args):
        name = args.name
        if not self.db.select_hako(name):
            raise NameError(f"Hako name '{name}' does not exist")
        docker_remove_container(name)
        self.db.remove_hako(name)
        print("finished!")
    
    def attach_hako(self, args):
        return
        

