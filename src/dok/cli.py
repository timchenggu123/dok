import argparse
import os
import sys
from dok.program import StateMachine

def docker_file(path="."):
    return os.path.abspath(path)

def create_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.create_dok(args)

def attach_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.attach_dok(args)

def remove_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.remove_dok(args)

def activate_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.activate_dok(args)

def activate_attach_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.activate_dok(args)
    program.attach_dok(args)

def list_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.list_dok(args)

def exec_handle(parser):
    program = StateMachine()
    program.exec_dok(sys.argv[2:])
    
def status_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.show_active()
    
def deactivate_handle(parser):
    program = StateMachine()
    program.deactivate_dok()

def copy_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.copy_dok(args)

def docker_handle(parser):
    args, _ = parser.parse_known_args()
    program = StateMachine()
    program.docker_create_dok(args, sys.argv[2:])

def main():
    parser = argparse.ArgumentParser(
            prog = "dok", description="Quickly start your containerized dev environment."
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    activate_parser = subparsers.add_parser("activate", aliases=["a"])
    activate_parser.add_argument("name", default="", help="Name of the dok to use.")
    activate_parser.set_defaults(func=activate_handle)

    create_parser = subparsers.add_parser("create", aliases=["c"], help="Create a new dok dev environment.")
    create_parser.add_argument("name", type = str, help="Pass a custom name for the dok.")
    file_or_image = create_parser.add_mutually_exclusive_group(required=False)
    file_or_image.add_argument("-f", "--file", action="store_true", default = False, help="Explicitly specify that file_or_image is file.")
    file_or_image.add_argument("-i", "--image", action="store_true", default = False, help="Explicitly specify that file_or_image is an image.")
    create_parser.add_argument("file_or_image", type=str, default = None, help = "An image name or the path to a docker compose file. dok will try to determine automatically.")
    create_parser.add_argument("--run-args", type=str, default="", required=False, help = "Only needed when creating from image.Additional docker run arguments would you like to pass during container creation enclosed in quotation marks.")
    create_parser.set_defaults(func=create_handle)

    remove_parser = subparsers.add_parser("remove", aliases=["r"], help="Remove a dok environment.")
    remove_parser.add_argument("name", type=str, nargs="*", help="Name of the target dok to remove.")
    remove_parser.add_argument("--all", action="store_true", default=False, help="Remove ALL existing environments.")
    remove_parser.set_defaults(func=remove_handle)

    attach_parser = subparsers.add_parser("attach", aliases=['t'], help="Attach to the active dok environment.")
    # attach_parser.add_argument("command", nargs="?", default="/bin/bash", help="[optional] a list of commands to run after activation, enclosed as a string")
    activate_parser.add_argument("-p", "--privileged", action="store_true", default=False, help="Attach to the container in privileged mode.")
    attach_parser.set_defaults(func=attach_handle)

    activate_attach_parser=subparsers.add_parser("activate-attach", aliases=["at"], help="Combine the activate and attach commands.")
    activate_attach_parser.add_argument("name", type=str, help="Name of the dok to use.")
    activate_attach_parser.add_argument("-p", "--privileged", action="store_true", default=False, help="Attach to the container in privileged mode.")
    activate_attach_parser.set_defaults(func=activate_attach_handle)

    list_parser=subparsers.add_parser("list", aliases=["l"], help="List all available doks.")
    list_parser.set_defaults(func=list_handle)

    exec_parser=subparsers.add_parser("exec", aliases=["e"], help="Execute a single command in the active dok.")
    exec_parser.set_defaults(func=exec_handle)

    status_parser=subparsers.add_parser("status", aliases=["s"], help="Show active dok container.")
    status_parser.set_defaults(func=status_handle)
    
    deactivate_parser=subparsers.add_parser("deactivate", aliases=["d"], help="Deactivate the current dok.")
    deactivate_parser.set_defaults(func=deactivate_handle)

    copy_parser = subparsers.add_parser("copy", aliases=["cp"], help="Create a copy of an existing dok.")
    copy_parser.set_defaults(func=copy_handle)
    copy_parser.add_argument("source", type=str, help="The name of the source dok to copy from.")
    copy_parser.add_argument("name", type=str, help="The name of the new dok.")

    docker_parser = subparsers.add_parser("docker", help="Create a container from a native docker run command")
    docker_parser.set_defaults(func=docker_handle)

    args, _ = parser.parse_known_args() 
    args.func(parser)

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
        