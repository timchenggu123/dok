import argparse
import os
import sys
from hako.program import StateMachine

def docker_file(path="."):
    return os.path.abspath(path)

def create_handle(args):
    program = StateMachine()
    program.create_hako(args)

def attach_handle(args):
    program = StateMachine()
    program.attach_hako(args)

def remove_handle(args):
    program = StateMachine()
    program.remove_hako(args)

def activate_handle(args):
    program = StateMachine()
    program.activate_hako(args)

def activate_attach_handle(args):
    program = StateMachine()
    program.activate_hako(args)
    program.attach_hako(args)
    
def main():
    parser = argparse.ArgumentParser(
            prog = "hako", description="Quickly start your containerized dev environment."
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    activate_parser = subparsers.add_parser("activate", aliases=["a"])
    activate_parser.add_argument("name", default="", help="Name of the hako to use.")
    activate_parser.set_defaults(func=activate_handle)

    create_parser = subparsers.add_parser("create", aliases=["c"])
    create_parser.add_argument("name", type = str, help="Pass a custom name for the hako.")
    file_or_image = create_parser.add_mutually_exclusive_group()
    file_or_image.add_argument("-f", "--file", type = str, default = None, help="Specify a docker compose file to base the hako on.")
    file_or_image.add_argument("-i", "--image", type = str, default = None, help="Specify the docker image to base the hako on.")
    create_parser.add_argument("--run-args", type=str, default=None, required=False, help = "Pass in the additional docker run arguments would you like to pass, enclosed in quotation marks. Only works with the -i --image option.")
    create_parser.set_defaults(func=create_handle)

    remove_parser = subparsers.add_parser("remove", aliases=["rm"])
    remove_parser.add_argument("name", type=str, help="Name of the target hako to remove.")
    remove_parser.set_defaults(func=remove_handle)

    attach_parser = subparsers.add_parser("attach", aliases=['t'])
    # attach_parser.add_argument("command", nargs="?", default="/bin/bash", help="[optional] a list of commands to run after activation, enclosed as a string")
    attach_parser.set_defaults(func=attach_handle)

    activate_attach_parser=subparsers.add_parser("activate-attach", aliases=["at"])
    activate_attach_parser.add_argument("name", type=str, help="Name of the hako to use.")
    activate_attach_parser.set_defaults(func=activate_attach_handle)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
        