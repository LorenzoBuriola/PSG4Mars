# *******************************************************
# Lorenzo Buriola - University of Bologna - CNR-ISAC
# PSGpy - docker_utils.py
# Functions that make use of the docker SDK for pyhton
# to manage docker containers from within python apps
# *******************************************************

import docker
from docker.errors import NotFound, APIError

def is_container_running(name, url):
    """
    Check if a Docker container is running
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    docker_client = docker.DockerClient(base_url=url)
    try:
        container = docker_client.containers.get(name)
    except NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    except APIError as exc:
        print(f"API error occurred: {exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == "running"

def start_container(name, url) -> None:
    """
    Start a Docker container
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).start()

def stop_container(name, url) -> None:
    """
    Stop a Docker container
    
    Parameters
    ----------
    name: string - name of the container
    url: string - url of the container
    """
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).stop()