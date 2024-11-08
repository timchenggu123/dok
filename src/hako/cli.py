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

def main():
    parser = argparse.ArgumentParser(
            prog = "hako", description="Quickly start your containerized dev environment."
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    start_parser = subparsers.add_parser("activate", aliases=["a"])
    start_parser.add_argument("hako", default="", help="Name of the hako to use")

    create_parser = subparsers.add_parser("create", aliases=["c"])
    create_parser.add_argument("name", type = str, help="Pass a custom name for the hako")
    file_or_image = create_parser.add_mutually_exclusive_group()
    file_or_image.add_argument("-i", "--image", type = str, default = None, help="Specify the docker image to base the hako on")
    # file_or_image.add_argument("-f", "--file", type = str, default = None, help="Specify a docker compose file to base the hako on")
    create_parser.add_argument("--args", type=str, default="", help = "Pass in the additional docker run arguments would you like to pass, enclosed in quotation marks.")
    create_parser.set_defaults(func=create_handle)

    remove_parser = subparsers.add_parser("remove", aliases=["rm"])
    remove_parser.add_argument("name", type=str, help="Name of the target hako to remove")
    remove_parser.set_defaults(func=remove_handle)

    attach_parser = subparsers.add_parser("attach", aliases=['a'])
    attach_parser = attach_parser.set_defaults(func=attach_handle)


    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
        