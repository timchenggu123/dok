import subprocess as sb
import os, sys, shlex
from dok.utils import *
from dok import __windows__
from time import sleep
import yaml
import pathlib

DOK_MAPPING_DIR="dokmappingdir"
DOK_YAML_DIR = os.path.dirname(os.path.abspath(__file__))

def get_container_name(name):
    return f"dok-{name}"

def rebase_path(base, rel):
    path = os.path.join(base, rel)
    return os.path.abspath(path)

def get_host_user_group_id():    
    if not __windows__:
        uid = sb.run(["id", "-u"], capture_output=True).stdout.decode("utf-8").strip()
        gid = sb.run(["id", "-g"], capture_output=True).stdout.decode("utf-8").strip()
        return uid, gid
    return None, None

def parse_yaml(obj, name, yml_path):
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

    wkdir = os.path.dirname(os.path.abspath(yml_path))
    if len(obj['services'].items()) > 1:
        print("Multiple services found in the docker compose file. Please ensure there is only one.")
        sys.exit(-1)
    key, service = list(obj['services'].items())[0]
    obj["services"][get_container_name(name) + "-service"] = obj["services"].pop(key)
    service["container_name"] = get_container_name(name)

    if not DOK_MAPPING_DIR in service.get("volumes", []):
        if __windows__:
            # service["volumes"].append(f"/host_mnt:/{DOK_MAPPING_DIR}")
            pass
        else:
            service["volumes"].append(f"/:/{DOK_MAPPING_DIR}")
    paths = []
    for path in service["volumes"]:
        host_path, container_path = path.split(":")
        host_path = rebase_path(wkdir, host_path) 
        new_path = f"{host_path}:{container_path}"
        paths.append(new_path)
    service["volumes"] = paths

    build =  service.get("build", None)
    if build and build["context"]:
        context_path = build["context"]
        build["context"] = rebase_path(wkdir, context_path)
    if build and build["dockerfile"]:
        file_path = build["dockerfile"]
        build["dockerfile"] = rebase_path(wkdir, file_path)
    
    files = []
    if service.get("env_file", None):
        for file in service["env_file"]:
            files.append(rebase_path(wkdir, file))
        service["env_file"] = files
    
    entrypoint = service.get("entrypoint", [])
    entrypoint.extend(["/bin/sh", "-c"])
    command = service.get("command", "")
    if type(command) == list:
        command = " ".join(command)
    if command:
        print("WARNING: Found command field specified in the docker compose file. dok recommends executing all default commands with the entrypoint.")
    command = "\n".join([command, "/bin/sh"])
    service["command"] = [command]
    service["entrypoint"] = entrypoint
    
    service["tty"] = True
    service["stdin_open"] = True
    return obj

def parse_yaml_rename_only(obj, name):
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

    if len(obj['services'].items()) > 1:
        print("Multiple services found in the docker compose file. Please ensure there is only one.")
        sys.exit(-1)
    key, service = list(obj['services'].items())[0]
    obj["services"][get_container_name(name) + "-service"] = obj["services"].pop(key)
    service["container_name"] = get_container_name(name)
    return obj
    
def get_yaml_dir():
    dir = DOK_YAML_DIR
    yaml_dir = os.path.join(dir, "docker_compose")
    if not os.path.exists(yaml_dir):
        os.mkdir(yaml_dir)
    return yaml_dir

def save_yaml(obj, name):
    yaml_dir = get_yaml_dir()
    filepath = os.path.join(yaml_dir, f"{name}.yml")
    with open(filepath, "w") as f:
        yaml.safe_dump(obj, f)
    return filepath

def docker_get_shell(name):
    container_name = get_container_name(name)
    cmd = ["docker", "exec", "-i", container_name, "sh"]
    handle = sb.Popen(cmd, stdin=sb.PIPE, stderr=sb.PIPE, stdout=sb.PIPE)
    exe, _  = handle.communicate(input=b"command -v bash")
    return exe.decode("utf-8").strip() if handle.poll() == 0 else "sh"
    
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

def docker_container_create_user(name, uid):
    shell = docker_get_shell(name)
    container_name = get_container_name(name)
    cmd = ["docker", "exec", "--privileged", container_name, shell, "-c"]
    #Check if sudo is available as a command
    cmd.append("command -v sudo")
    handle = sb.Popen(cmd)
    handle.wait()
    sudo = ""
    if handle.returncode == 0:
        sudo = "sudo "
    #Find user id in the container
    cmd[-1] = f'grep ":{uid}:" /etc/passwd'
    handle = sb.Popen(cmd, stdout=sb.PIPE)
    handle.wait()
    if handle.returncode != 0:
        user_name = ""
    else:
        user_name = handle.stdout.read().decode("utf-8").strip().split(":")
    if not user_name:
        #Create a user
        if shell != "sh":
            cmd[-1] = f"{sudo}useradd -u {uid} -m -s {shell} dok"
        else:
            cmd[-1] = f"{sudo}useradd -u {uid} -m dok"
        handle = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
        handle.wait()
        if handle.returncode != 0:
            return False
        user_name = "dok"
    else:
        print("INFO: Found user in container with the same user id as host. Using it as default dok user.")
        user_name = user_name[0]
    
    cmd[-1] = f"{sudo}groups"
    handle = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
    handle.wait()
    groups = handle.stdout.read().decode("utf-8").strip().split()
    cmd[-1] = sudo + shlex.join(["usermod", "-a", "-G", ",".join(groups), user_name])
    handle = sb.Popen(cmd)
    handle.wait()
    return True

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

def docker_stop_container_async(name):
    container_name = get_container_name(name)
    cmd = ["docker", "stop", container_name]
    sb.Popen(cmd, stdout=sb.PIPE)

def docker_remove_container(name):
    if docker_is_container_running(name):
        docker_stop_container(name)
    container_name = get_container_name(name)
    cmd = ["docker", "container", "rm", container_name]
    handle = sb.Popen(cmd, stdout=sb.PIPE, stderr=sb.PIPE)
    animation = WaitingAnimation("Removing container")
    animation.update()
    while handle.poll() is None:
        sleep(0.2)
        animation.update()
    if handle.poll() < 0:
        print("Failed to remove container...")
        print("Error:")
        err = handle.stderr.read().decode("utf-8")
        print(err)
        sys.exit(1)
    out = handle.stdout.read().decode("utf-8").strip()
    if out != container_name:
        animation.finish(f"Failed to remove container '{name}'\n..skip")
        return
    animation.finish("success!")

def docker_compose_create_container(file_path, name):
    if docker_container_exists(name):
        yes = input(f"Found conflicting container. Do you want to remove the container <{get_container_name(name)}> and retry? [Y/N]\n")
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
        err=handle.stderr.read().decode("utf-8")
        out=handle.stdout.read().decode("utf-8") 
        print(f"Cannot bring up container...")
        print(f"Error:")
        print(out)
        print(err)
        print("Cleaning up...")
        if docker_container_exists(name): docker_remove_container(name)
        sys.exit(1)
    if not __windows__:
        print("Creating dok user...", end="\r")
        uid, _ = get_host_user_group_id()
        if docker_container_create_user(name, uid):
            print("Creating dok user...success!") 
        else:
            print("Creating dok user...skipped")
    animation.finish("success!")

def docker_create_container(name, image, docker_args, docker_command):
    if docker_container_exists(name):
        yes = input(f"Found conflicting container. Do you want to remove the container <{get_container_name(name)}> and retry? [Y/N]")
        if yes.lower() == "y":
            docker_remove_container(name)
            cmd = docker_create_container(name, image, docker_args, docker_command)
            return cmd
        print("aborted")
        sys.exit(-1)
    cmd = ["docker", "run"]
    container_name = get_container_name(name)
    
    #These can be overriden by the user-specified flags
    if __windows__:
        cmd.extend(["--volume", "/host_mnt:/dokmappingdir"])
    else:
        cmd.extend(["--volume", "/:/dokmappingdir"])
    
    #Removing illegal flags.
    docker_args = shlex.split(docker_args.strip())
    for arg in docker_args:
        if arg == "-it":
            docker_args.remove(arg)
            print("INFO: Found illegal docker flag '-it'. Ignoring since Dok will handle TTY automatically ;)")

    cmd.extend(docker_args)

    #These cannot be overriden
    cmd.extend(["--name", f"{container_name}"])

    cmd.extend(["-t", f"{image}"])
    cmd.extend(shlex.split(docker_command.strip()))
    handle = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE, stdin=sb.PIPE)
    animation = WaitingAnimation("Creating dok")
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
    if not __windows__:
        print("Creating dok user...", end="\r")
        uid, _ = get_host_user_group_id()
        if docker_container_create_user(name, uid):
            print("Creating dok user...success!")
        else:
            print("Creating dok user...skipped")
    return cmd

def docker_copy_from_command(name, cmd):
    cmd = shlex.split(cmd.strip())

    # Reset the container name
    for i,v  in enumerate(cmd):
        if v == "--name":
            break
    cmd[i+1] = get_container_name(name)
    handle = sb.Popen(cmd, stderr=sb.PIPE, stdout=sb.PIPE, stdin=sb.PIPE)
    animation = WaitingAnimation("Creating dok")
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
    if not __windows__:
        print("Creating dok user...", end="\r")
        uid, _ = get_host_user_group_id()
        if docker_container_create_user(name, uid):
            print("Creating dok user...success!")
        else:
            print("Creating dok user...skipped")
    return cmd
    
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
        print("\nError trying to start docker container. Was it accidentally removed? Try remove the dok and create it again.")
        print("Error:")
        err = handle.stderr.read().decode("utf-8")
        print(err)
    animation.finish("success!")

def get_docker_pwd():
    if __windows__:
        pwd = pathlib.PureWindowsPath(os.getcwd())
        drive = pwd.drive.replace(":", "").lower()
        path = pwd.parts[1:]
        pwd = pathlib.PurePosixPath("/", drive, *path)
    else:
        pwd = os.path.abspath(os.curdir)
    pwd = "".join(["/", DOK_MAPPING_DIR, str(pwd)])
    return pwd

def docker_attach_container(name, privileged=False):
    shell = docker_get_shell(name)
    container_name = get_container_name(name)
    cmd = ["docker", "exec", "-it"]
    if privileged:
        cmd.extend(["--privileged"])
    else:
        if not __windows__:
            uid, gid = get_host_user_group_id()
            cmd.extend(["-u", f"{uid}:{gid}"])
    cmd.append(container_name)
    dok_pwd = get_docker_pwd()
    dok_pwd = dok_pwd.replace(" ", "\\ ")
    if not __windows__:
        cmd.extend(shlex.split(f"{shell} -c 'cd {dok_pwd} && {shell}'"))
    else:
        cmd.extend(shlex.split(f"{shell}"))
    sb.run(cmd)
    
def docker_exec_command(name, argv, privileged=False):
    shell = docker_get_shell(name)
    container_name = get_container_name(name)
    cmd = ["docker", "exec", "-it"]
    if not privileged:
        if not __windows__:
            uid, gid = get_host_user_group_id()
            cmd.extend(["-u", f"{uid}:{gid}"])
    cmd.append(container_name)
    dok_pwd = get_docker_pwd()
    dok_pwd = dok_pwd.replace(" ", "\\ ")
    command = shlex.join(argv)
    if not __windows__:
        cmd.extend([shell, "-c", f"cd '{dok_pwd}' && " + command])
    else:
        cmd.extend([shell])
    sb.run(cmd)
