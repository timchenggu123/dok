from hako.db import Database 
from hako.interface import *

class StateMachine():
    def __init__(self):
        '''
        This is the main statemachine of the program.
        responsible for state persistence across runs
        '''
        self.db = Database()
    
    def run(self, args):
        if args.command in ["create", "c"]:
            name = args.name
            if self.db.select_hako(name):
                raise NameError(f"Hako {name} already exists")
            if args.image:
                self.create_hako_from_image(args) 
                return
            raise ValueError("Please specify an image.")
    
    def create_hako_from_image(self, args):
        image = args.image
        name  = args.name
        docker_args = args.args
        docker_create_container(name, image, docker_args)
        self.db.insert_hako(name, image ,docker_args, "") 
        

