# HAKO
`hako` is a command line tool that helps streamline your workflow with containerized dev environments. Inspired by `conda`, `hako` wraps around `docker` and `docker-compose` to help you seamlessly swap between bare-metal and containerized environments.

## Elevator Pitch
Docker is great. Using docker containers as dev environments is a brilliant idea. But it can also be a just a little bit annoying -- we all go through the tedious `docker run -it`'s, the `--user`'s, the `--volumes ./:`, and the more-than-long-enough list of arguments just to get a container running. Oh what, can't attach because the entrypoint automatically exit? Better re-run `docker run` with `/bin/bash` at the end then. Oh that didnt' work because it is `alpine` based, gotta use `sh`. After a bit of tweaking you managed to get it to work, but you forgot to name your container so next time you try to use it you had to run `docker ps -a` and get confused if it was `awesome_shamir` or `epic_lamarr`. Finally, you manged to find the right one, you run `docker start -ai` but it didn't work, so you resort to `docker start` followed by `docker attach`. Input not work. Exasperated, you type `docker exec -it epic_lammar sh`, and viola! You are finally in.

Fine, maybe you are smart and organized, and you use `docker compose`, so it is all good and managed. But it still can be an annoying to configure `volumes`, `stdin`, `tty`, `user` everytime in the yaml, oh and don't forget to put a `/bin/bash -c "sleep infinity"` in the command to keep the container alive! *What? `Alpine`? Not again!* After all this work, you still have to run `docker compose up -d && docker exec -it <name> /bin/bash` just to run it. 

Okay, maybe it is not that bad, but still, this can be much simpler. `hako` simplies the work you need to do to manage your dev environments; it merges multiple commands together and automatically add commonly use flags to the commands. It ensures containers do not auto exit and automatically select and attach to available shells with concise commands. It will even cd to a mounted directory for you! 
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
