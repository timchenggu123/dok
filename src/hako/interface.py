from subprocess import run
import os

HAKO_MAPPING_DIR="hakomappingdir"

def get_hako_name(name):
    return f"hako-{name}"

def docker_create_container(name, image, args):
    cmd = ["docker", "run"]
    container_name = get_hako_name(name)
    cmd.extend(["--name", f"{container_name}"])
    cmd.extend(["--volume", "/:/hakomappingdir"])
    cmd.extend(args.strip().split())
    cmd.extend([f"{image}"])
    cmd.extend(["sleep", "infinity"])
    " ".join(cmd)
    print(cmd)
    run(cmd)
