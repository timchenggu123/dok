# ROCm Pytorch Example

This shows how to start a rocm/pytorch dev environment using Hako. The included docker file configures everything required to enable AMD GPU access.

### To create the environment, run
```bash
hako c myenv ./docker-compose.yml
```
**Note*: creating the environment for the first time might take a while since docker will have to pull the image. Alternatively, you can run `docker pull rocm/pytorch` before running this command. 

**Bonus*: this docker-compose file will automatically configure your github identity for you. Navigate to the "command" field in the docker compose file and modify it with your own identity.

### To attach to the environment, run 
```bash
hako at myenv
```