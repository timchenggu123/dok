# DOK
`dok` is a command line tool that helps streamline your workflow with containerized dev environments. Inspired by `conda`, `dok` wraps around `docker` and `docker-compose` to help you seamlessly swap between bare-metal and containerized environments.

## Elevator Pitch
Docker is a really powerful tool and great for developing and testing software in different environments. However, the process of using a docker container can be simpler. Take a look at the following docker command for using ROCm with docker
```
docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
--device=/dev/kfd --device=/dev/dri --group-add video \
--ipc=host --shm-size 8G rocm/pytorch:latest
```
 This needs to be run everytime a new container needs to be created, which can be a bit of a pain. If only there some way to quickly copy the configuration of existing containers can create new ones.

 With dok, you can! Simply prepend dok to the docker command
 ```
 dok docker run -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
--device=/dev/kfd --device=/dev/dri --group-add video \
--ipc=host --shm-size 8G rocm/pytorch:latest
```
And give the resulting dok a name such as `mario`

Now, everytime you want a fresh container with the same configuration, just run
```
dok cp mario luigi
```

Dok offers many more awesome features like this, check it out!

### Requirements:
`docker` >= 27.0.0 and `python` >= 3.8

### Instruction:
```bash
git clone https://github.com/timchenggu123/dok.git && cd dok && pip install .
```

## Quick start
## Creating a dok
`create` a dok container from your `docker run` command
```bash
dok docker run <your flags and commands here>
```
Enter a name for your dok container after the promt
```
Please enter a name for the image you are creating.
mydok
```
## Using a dok container
Once it is ready, `a`ctivate and a`t`tach to `mydok` with.
```bash
dok at mydok
```
To exit the environment, simply type `exit`. 

To a`t`tach to the dev environemnt again, just type
```bash
dok t
```
To attach as root user, append `-p`
```
dok t -p
```
Alternatively, if you just want to `e`xecute something without having to attach to the container, run
```bash
dok e <your command>
```
For example,
```bash
dok e echo "Hello World!"
```
