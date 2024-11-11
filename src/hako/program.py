from hako.db import Database 
from hako.interface import *
import sys, yaml

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
        if args.file:
            self.create_hako_from_file(args)
            return
        raise ValueError("Please specify an image.")
    
    def create_hako_from_file(self,args):
        name = args.name
        file_path = os.path.abspath(args.file)
        p = os.path.abspath(file_path)
        print("Loading docker-compose file...")
        with open(p, "r") as f:
            obj = yaml.safe_load(f)
        print("Parsing docker-compose file")
        obj = parse_yaml(obj, name)
        f = save_yaml(obj, name)
        print(f"Hako docker-compose file saved to {f}")
        docker_compose_create_container(f, name)
        self.db.insert_hako(name, "", "", docker_file=file_path)
        print("success!")
    
    def create_hako_from_image(self, args):
        image = args.image
        name  = args.name
        docker_args = args.args
        docker_command = "sleep infinity"
        docker_create_container(name, image, docker_args, docker_command)
        self.db.insert_hako(name, image, docker_args, docker_command) 

    def remove_hako(self, args):
        name = args.name
        if not self.db.select_hako(name):            
            print(f"Hako named '{name}' does not exist. To learn about how to create a hako, see")
            print(f"    hako create --help")
            sys.exit(-1)
        if self.db.select_active_hako() == name:
            print("Deactivating container...sucess!")
            self.db.deactivate_hako()
        docker_remove_container(name)
        self.db.remove_hako(name)
        print("finished!")
    
    def activate_hako(self, args):
        name = args.name
        if not self.db.select_hako(name):
            print(f"Hako named '{name}' does not exist. To learn about how to create a hako, see")
            print(f"    hako create --help")
            sys.exit(-1)
        docker_start_container(name)
        self.db.replace_active_hako(name)
        print("Activated hako!")
        
    def attach_hako(self, args):
        name = self.db.select_active_hako()
        if name is None:
            print("No hako is active currently. To learn about how to activate a hako, see")
            print("     hako activate --help")
            sys.exit(-1)
        if not docker_is_container_running(name):
            docker_start_container(name)
        docker_attach_container(name)
