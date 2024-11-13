import argparse
import os
import sys
from hako.program import StateMachine

def docker_file(path="."):
    return os.path.abspath(path)

def create_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.create_hako(args)

def attach_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.attach_hako(args)

def remove_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.remove_hako(args)

def activate_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.activate_hako(args)

def activate_attach_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.activate_hako(args)
    program.attach_hako(args)

def list_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.list_hako(args)

def exec_handle(parser):
    program = StateMachine()
    program.exec_hako(sys.argv[2:])
    
def status_handle(parser):
    args = parser.parse_args()
    program = StateMachine()
    program.show_active(args)
    
def main():
    parser = argparse.ArgumentParser(
            prog = "hako", description="Quickly start your containerized dev environment."
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    activate_parser = subparsers.add_parser("activate", aliases=["a"])
    activate_parser.add_argument("name", default="", help="Name of the hako to use.")
    activate_parser.set_defaults(func=activate_handle)

    create_parser = subparsers.add_parser("create", aliases=["c"], help="Create a new hako dev environment.")
    create_parser.add_argument("name", type = str, help="Pass a custom name for the hako.")
    file_or_image = create_parser.add_mutually_exclusive_group(required=False)
    file_or_image.add_argument("-f", "--file", action="store_true", default = False, help="Explicitly specify that file_or_image is file.")
    file_or_image.add_argument("-i", "--image", action="store_true", default = False, help="Explicitly specify that file_or_image is an image.")
    create_parser.add_argument("file_or_image", type=str, default = None, help = "An image name or the path to a docker compose file. Hako will try to determine automatically.")
    create_parser.add_argument("--run-args", type=str, default="", required=False, help = "Only needed when creating from image.Additional docker run arguments would you like to pass during container creation enclosed in quotation marks.")
    create_parser.set_defaults(func=create_handle)

    remove_parser = subparsers.add_parser("remove", aliases=["r"], help="Remove a hako environment.")
    remove_parser.add_argument("name", type=str, help="Name of the target hako to remove.")
    remove_parser.set_defaults(func=remove_handle)

    attach_parser = subparsers.add_parser("attach", aliases=['t'], help="Attach to the active hako environment.")
    # attach_parser.add_argument("command", nargs="?", default="/bin/bash", help="[optional] a list of commands to run after activation, enclosed as a string")
    attach_parser.set_defaults(func=attach_handle)

    activate_attach_parser=subparsers.add_parser("activate-attach", aliases=["at"], help="Combine the activate and attach commands.")
    activate_attach_parser.add_argument("name", type=str, help="Name of the hako to use.")
    activate_attach_parser.set_defaults(func=activate_attach_handle)

    list_parser=subparsers.add_parser("list", aliases=["l"], help="List all available hakos.")
    list_parser.set_defaults(func=list_handle)

    exec_parser=subparsers.add_parser("exec", aliases=["e"], help="Execute a single command in the active hako.")
    exec_parser.set_defaults(func=exec_handle)

    status_parser=subparsers.add_parser("status", aliases=["s"], help="Show active hako container.")
    status_parser.set_defaults(func=status_handle)
    args, _ = parser.parse_known_args() 
    args.func(parser)

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
        