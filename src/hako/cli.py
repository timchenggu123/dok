import argparse
import os
import sys
from hako.program import StateMachine

def docker_file(path="."):
    return os.path.abspath(path)

def main():
    parser = argparse.ArgumentParser(
            prog = "hako", description="Quickly start your containerized dev environment."
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    start_parser = subparsers.add_parser("start", aliases=["s"],)
    start_parser.add_argument("hako/image name", default="", help="Name of the hako/image to use")

    create_parser = subparsers.add_parser("create", aliases=["c"])
    create_parser.add_argument("name", type = str, help="Pass a custom name for the hako")
    create_parser.add_argument("-i", "--image", type = str, default = None, help="Specify the docker image to base the hako on")
    create_parser.add_argument("--args", type=str, default="", help = "Pass in the additional docker run arguments would you like to pass, enclosed in quotation marks.")

    remove_parser = subparsers.add_parser("remove", aliases=["rm"])
    remove_parser.add_argument("name", type=str, help="Name of the target hako to remove")

    args = parser.parse_args()
    print(args)
    program = StateMachine()
    program.run(args)


if __name__ == "__main__":
    main()
        