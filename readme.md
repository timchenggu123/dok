# HAKO
`hako` is a command line tool that helps streamline your workflow with containerized dev environments. Inspired by `conda`, `hako` wraps around `docker` and `docker-compose` to help you seamlessly swap between bare-metal and containerized environments.

## Installation
### Requirements:
`docker` >= 27.0.0 and `python` >= 3.8

### Instruction:
```bash
git clone https://github.com/timchenggu123/hako.git && cd hako && pip install .
```

## Quick start
### Creating a Ubuntu dev environment
`create` a Ubuntu dev environment simply with
```bash
hako c myhako -i alphine
```
This will create a container from the `alphine:latest` image.

Once it is ready, `activate` and `attach` to the environment with.
```bash
hako at myhako
```
To exit the environment, simply type `exit`. 

To `attach` to the dev environemnt again, just type
```bash
hako t
```
Alternatively, if you just want to `execute` something without having to attach to the container, run
```bash
hako e <your command>
```
For example,
```bash
hako e echo "Hello World!"
```
