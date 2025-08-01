from dok.db import Database 
from dok.interface import *
import sys, yaml, shutil

class StateMachine():
    def __init__(self):
        '''
        This is the main statemachine of the program.
        responsible for state persistence across runs
        '''
        self.db = Database()
    
    def create_dok(self, args):
        name = args.name
        if self.db.select_dok(name):
            print(f"dok named '{name}' already exists.")
            yes = input(f"Do you want to replace '{name}'? [Y/N]\n")
            if yes.lower() != "y":
                print("aborted!")
                sys.exit(-1)
            docker_remove_container(name)
            self.db.remove_dok(name)
        if args.image:
            args.image = args.file_or_image
            self.create_dok_from_image(args) 
            return
        if args.file:
            args.file = args.file_or_image
            self.create_dok_from_file(args)
            return
        if os.path.exists(args.file_or_image):
            args.file = args.file_or_image
            self.create_dok_from_file(args)
            return
        args.image = args.file_or_image
        self.create_dok_from_image(args)
    
    def create_dok_from_file(self,args):
        name = args.name
        file_path = os.path.abspath(args.file)
        p = os.path.abspath(file_path)
        print("Loading docker-compose file...")
        with open(p, "r") as f:
            obj = yaml.safe_load(f)
        print("Parsing docker-compose file")
        obj = parse_yaml(obj, name, file_path)
        f = save_yaml(obj, name)
        print(f"dok docker-compose file saved to {f}")
        docker_compose_create_container(f, name)
        self.db.insert_dok(name, "", "", docker_file=file_path)
        print("finished!")
    
    def create_dok_from_image(self, args):
        image = args.image
        name  = args.name
        docker_args = args.run_args
        docker_command = "sleep infinity"
        cmd = docker_create_container(name, image, docker_args, docker_command)
        cmd = " ".join(cmd)
        self.db.insert_dok(name, image, cmd, "")
        print("finished!")

    def remove_dok(self, args):
        names = []
        if args.all:
            yes = input(f"This will remove ALL dok environments and docker containers. Are you sure [Y/N]\n").lower()
            if yes != "y":
                exit(1)
            names=self.db.select_all_dok()
        else:
            names = args.name
        if names == []:
            print(f"No dok name provided. See `dock remove --help for usage.")
            exit(1)
        for name in names:
            if not self.db.select_dok(name):            
                print(f"dok named '{name}' does not exist. To learn about how to create a dok, see")
                print(f"    dok create --help")
                sys.exit(-1)
            if self.db.select_active_dok() == name:
                print("Deactivating container...success!")
                self.db.deactivate_dok()
            docker_remove_container(name)
            self.db.remove_dok(name)
        print("finished!")
    
    def activate_dok(self, args):
        name = args.name
        if not self.db.select_dok(name):
            print(f"dok named '{name}' does not exist. To learn about how to create a dok, see")
            print(f"    dok create --help")
            sys.exit(-1)
        docker_start_container(name)
        active_dok = self.db.select_active_dok()
        if active_dok != name:
            docker_stop_container_async(active_dok)
            self.db.replace_active_dok(name)
        print("Activated dok!")
        
    def attach_dok(self, args):
        name = self.db.select_active_dok()
        print(f"[dok]: Attaching to '<{name}>'")
        if name is None:
            print("No dok is active currently. To learn about how to activate a dok, see")
            print("     dok activate --help")
            sys.exit(-1)
        if not docker_is_container_running(name):
            docker_start_container(name)
        docker_attach_container(name, privileged=args.privileged)
    
    def list_dok(self, args):
        active_dok = self.db.select_active_dok()
        active_dok = self.db.select_dok(active_dok)
        doks = self.db.select_all_dok()
        print("Name\tStatus\tImage\tFile".expandtabs(16))
        if not (active_dok is None):
            print(f"{active_dok[0]}\tActive\t{active_dok[1]}\t{active_dok[-1]}".expandtabs(16))
        for line in doks:
            if active_dok and line[0] == active_dok[0]:
                continue
            print(f"{line[0]}\tInactive\t{line[1]}\t{line[-1]}".expandtabs(16))

    def exec_dok(self, argv):
        name = self.db.select_active_dok()
        if name is None:
            print("No dok is active currently. To learn about how to activate a dok, see")
            print("     dok activate --help")
            sys.exit(-1)
        if not docker_is_container_running(name):
            docker_start_container(name)
        docker_exec_command(name, argv)
    
    def show_active(self):
        name = self.db.select_active_dok()
        if name is None:
            print("No dok is active currently. To learn about how to activate a dok, see")
            print("     dok activate --help") 
            return
        print(name)
    
    def deactivate_dok(self):
        name = self.db.select_active_dok()
        if name is None:
            return
        docker_stop_container(name)
        self.db.deactivate_dok()
        print(f"Deactivated dok `{name}`")
        return
    
    def copy_dok(self, args):
        name = args.name
        if self.db.select_dok(name):
            print(f"dok named '{name}' already exists.")
            yes = input(f"Do you want to replace '{name}'? [Y/N]\n")
            if yes.lower() != "y":
                print("aborted!")
                sys.exit(-1)
            docker_remove_container(name)
            self.db.remove_dok(name)
        source = args.source
        _, image, cmd, file = self.db.select_dok(source)
        if cmd:
            docker_copy_from_command(name, cmd)
            self.db.insert_dok(name, image, cmd, "")
        if file:
            source_file = os.path.join(get_yaml_dir(), f"{source}.yml")
            with open(source_file, "r") as f:
                obj = yaml.safe_load(f)
            obj = parse_yaml_rename_only(obj, name)
            save_yaml(obj, name)
            dest_file = os.path.join(get_yaml_dir(), f"{name}.yml")
            docker_compose_create_container(dest_file, name)
            self.db.insert_dok(name, "", "", docker_file=dest_file)
        print("finished!")
    
    def docker_create_dok(self, args, argv):
        # Parse cmd options
        if argv.pop(0) != "run":
            print("Please enter a docker run command. Other docker commands are not supported by Dok :)")
            return
        args.name = input("Please enter a name for the image you are creating.\n")
        options = []
        f_option = False
        for arg in argv:
            if arg[0] == "-":
                options.append(arg)
                f_option = True
                continue
            if f_option:
                options.append(arg)
                f_option = False
                continue
            args.image = arg
            break
        args.run_args = shlex.join(options)
        self.create_dok_from_image(args)
        

