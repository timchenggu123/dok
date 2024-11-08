import subprocess as sb
import os, sys
from hako.utils import *
from time import sleep

HAKO_MAPPING_DIR="hakomappingdir"

def get_container_name(name):
    return f"hako-{name}"
    
def docker_create_container(name, image, docker_args, docker_command):
    cmd = ["docker", "run"]
    container_name = get_container_name(name)
    cmd.extend(["--name", f"{container_name}"])
    cmd.extend(["--volume", "/:/hakomappingdir"])

    uid = sb.run(["id", "-u"], capture_output=True).stdout.decode("utf-8").strip()
    gid = sb.run(["id", "-g"], capture_output=True).stdout.decode("utf-8").strip()
    cmd.extend(["--user", f"{uid}:{gid}"])

    cmd.extend(docker_args.strip().split())
    cmd.extend(["-t", f"{image}"])
    cmd.extend(docker_command.strip().split())
    
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
        print("Encountered  error trying to create hako: \n", err)
        sys.exit(-1)
    animation.finish("success!")

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
    
    
    