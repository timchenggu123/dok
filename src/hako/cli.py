import argparse
import os
import sys

def docker_file(path):
    return os.path(path)

def main():
    parser = argparse.ArgumentParser(
            prog = "hako", description="Quickly start your containerized dev environment"
            )
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    start_parser = subparsers.add_parser("start", aliases=["s"],)
    start_parser.add_argument("hako/image name", default="", help="Name of the hako/image to use")

    create_parser = subparsers.add_parser("create", aliases=["c"])
    create_parser.add_argument("-f", "--file", type = docker_file, nargs=1, help="Specify the path to docker file")
    create_parser.add_argument("-n", "--name", type = str, nargs=1, help="Pass a custom name for the hako")

    remove_parser = subparsers.add_parser("remove", aliases=["rm"])
    remove_parser.add_argument("name", type=str, help="Name of the target hako to remove")

    args = parser.parse_args()
    print(args)

if __name__ == "__main__":
    main()


    
    

        