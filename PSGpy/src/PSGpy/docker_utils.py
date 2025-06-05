# docker management functions (does not work on machines)

import docker
from docker.errors import NotFound, APIError


def is_container_running(name, url):
    RUNNING = "running"
    docker_client = docker.DockerClient(base_url=url)
    try:
        container = docker_client.containers.get(name)
    except NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    except APIError as exc:
        print(f"API error occurred: {exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING

def start_container(name, url) -> None:
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).start()

def stop_container(name, url) -> None:
    docker_client = docker.DockerClient(base_url=url)
    docker_client.containers.get(name).stop()