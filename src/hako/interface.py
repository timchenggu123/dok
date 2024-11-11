import subprocess as sb
import os, sys, shlex
from hako.utils import *
from time import sleep
import yaml

HAKO_MAPPING_DIR="hakomappingdir"
HAKO_YAML_DIR = os.path.dirname(os.path.abspath(__file__))

def get_container_name(name):
    return f"hako-{name}"

def parse_yaml(obj, name):
    if len(obj['services'].items()) > 1:
        print("Multiple services found in the docker compose file. Please ensure there is only one.")
        sys.exit(-1)
    service = obj["services"][list(obj['services'].items())[0][0]]
    service["container_name"] = get_container_name(name)

    if not HAKO_MAPPING_DIR in service.get("volumes", []):
        service["volumes"].append(f"/:/{HAKO_MAPPING_DIR}")
    paths = []
    for path in service["volumes"]:
        host_path, container_path = path.split(":")
        host_path = os.path.abspath(host_path)
        new_path = f"{host_path}:{container_path}"
        paths.append(new_path)
    service["volumes"] = paths

    build =  service.get("build", None)
    if build and build["context"]:
        context_path = build["context"]
        build["context"] = os.path.abspath(context_path)
    if build and build["dockerfile"]:
        file_path = build["dockerfile"]
        build["dockerfile"] = os.path.abspath(file_path)
    
    files = []
    if service.get("env_file", None):
        for file in service["env_file"]:
            files.append(os.path.abspath(file))
        service["env_file"] = files
    
    uid = sb.run(["id", "-u"], capture_output=True).stdout.decode("utf-8").strip()
    gid = sb.run(["id", "-g"], capture_output=True).stdout.decode("utf-8").strip()
    service["user"] = f"{uid}:{gid}"
    return obj

def save_yaml(obj, name):
    dir = HAKO_YAML_DIR
    yaml_dir = os.path.join(dir, "docker_compose")
    if not os.path.exists(yaml_dir):
        os.mkdir(yaml_dir)
    filepath = os.path.join(yaml_dir, f"{name}.yml")
    with open(filepath, "w") as f:
        yaml.safe_dump(obj, f)
    return filepath

def docker_container_exists(name):
    cmd = ["docker", "ps", "-a"]
    container_name = get_container_name(name)
    handle = sb.Popen(cmd, stdout=sb.PIPE)
    handle.wait()
    ret=handle.stdout.read().decode("utf-8").strip().split("\n")
    for line in ret:
        if container_name == line.split()[-1]:
            return True
    return False

    
def docker_is_container_running(name):
    cmd = ["docker", "ps"]
    container_name = get_container_name(name)
    handle = sb.Popen(cmd, stdout=sb.PIPE)
    handle.wait()
    ret=handle.stdout.read().decode("utf-8").strip().split("\n")
    for line in ret:
        if container_name == line.split()[-1]:
            return True
    return False

def docker_stop_container(name):
    container_name = get_container_name(name)
    cmd = ["docker", "stop", container_name]
    handle = sb.Popen(cmd, stdout=sb.PIPE)
    animation = WaitingAnimation(f"Stopping the container for '{name}'")
    animation.update()
    while handle.poll() is None:
        sleep(0.2)
        animation.update()
    ret=handle.stdout.read().decode("utf-8").strip()
    if ret != container_name:
        print("Failed to stop container '{name}'\n", ret)
        sys.exit(-1)
    animation.finish("success!")

def docker_remove_container(name):
    if docker_is_container_running(name):
        docker_stop_container(name)
    container_name = get_container_name(name)
    cmd = ["docker", "container", "remove", container_name]
    handle = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
    animation = WaitingAnimation("Removing container")
    animation.update()
    while handle.poll() is None:
        sleep(0.2)
        animation.update()
    animation.finish("success!")

def docker_compose_create_container(file_path, name):
    if docker_container_exists(name):
        yes = input(f"Found conflicting container. Do you want to remove the container <{get_container_name(name)}> and retry? [Y/N]")
        if yes.lower() == "y":
            docker_remove_container(name)
            docker_compose_create_container(file_path, name)
            return
        print("aborted.") 
        sys.exit(-1)
    cmd = ["docker", "compose"]
    cmd.extend(["-f", f"{file_path}"])
    cmd.extend(["up", "-d"])

    handle = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE)
    animation = WaitingAnimation(f"Creating the container for '{name}'")
    animation.update()
    while handle.poll() is None:
        sleep(0.2)
        animation.update()
    if handle.poll() < 0:
        err=handle.stderr.read().decode("utf-8")
        print(f"Failed to create container from yaml file...")
        print(f"Error:")
        print(err)
        sys.exit(1)
    if not docker_is_container_running(name):
        err=handle.stdout.read().decode("utf-8")
        print(f"Failed to create container from yaml file...")
        print(f"Error:")
        print(err)
        print("Cleaning up...")
        if docker_container_exists(name): docker_remove_container(name)
        sys.exit(1)
    animation.finish("success!")

def docker_create_container(name, image, docker_args, docker_command):
    if docker_container_exists(name):
        yes = input(f"Found conflicting container. Do you want to remove the container <{get_container_name(name)}> and retry? [Y/N]")
        if yes.lower() == "y":
            docker_remove_container(name)
            docker_create_container(name, image, docker_args, docker_command)
            return
        print("aborted")
        sys.exit(-1)
    cmd = ["docker", "run"]
    container_name = get_container_name(name)
    cmd.extend(["--name", f"{container_name}"])
    cmd.extend(["--volume", "/:/hakomappingdir"])

    uid = sb.run(["id", "-u"], capture_output=True).stdout.decode("utf-8").strip()
    gid = sb.run(["id", "-g"], capture_output=True).stdout.decode("utf-8").strip()
    cmd.extend(["--user", f"{uid}:{gid}"])

    cmd.extend(shlex.split(docker_args.strip()))
    cmd.extend(["-t", f"{image}"])
    cmd.extend(shlex.split(docker_command.strip()))

    handle = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE, stdin=sb.PIPE)
    animation = WaitingAnimation("Creating hako")
    animation.update()
    is_running = docker_is_container_running(name)
    is_finished = handle.poll()
    while not is_running and is_finished is None:
        sleep(0.2)
        animation.update()
        is_running = docker_is_container_running(name)
        is_finished = handle.poll()
    if is_finished:
        err = handle.stderr.read().decode("utf-8")
        print("Failed trying to create container: \n Error: \n", err)
        print("Cleaning up...")
        if docker_container_exists(name): docker_remove_container(name)
        sys.exit(-1)
    animation.finish("success!")

def docker_start_container(name):
    if docker_is_container_running(name):
        return
    container_name = get_container_name(name)
    cmd = ["docker", "start", container_name]
    handle = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
    animation = WaitingAnimation("Activating container")
    animation.update()
    while handle.poll() is None:
        sleep(0.2)
        animation.update()
    if handle.poll() < 0:
        print("\nError trying to start docker container. Was it accidentally removed? Try remove the hako and create it again.")
        print("Error:")
        err = handle.stderr.read().decode("utf-8")
        print(err)
    animation.finish("success!")

def docker_attach_container(name):
    container_name = get_container_name(name)
    cmd = ["docker", "exec", "-it", container_name]
    pwd = os.path.abspath(os.curdir)
    hako_pwd = "/" + HAKO_MAPPING_DIR + str(pwd)
    cmd.extend(shlex.split(f"/bin/bash -c 'cd {hako_pwd} && bash'"))
    sb.run(cmd)

    
    
    
    