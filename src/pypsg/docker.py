# docker management functions (does not work on machines)

import docker

def is_container_running(name):
    RUNNING = "running"
    docker_client = docker.from_env()
    try:
        container = docker_client.containers.get(name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING

def start_container(name) -> None:
    docker_client = docker.from_env()
    docker_client.containers.get(name).start()

def stop_container(name) -> None:
    docker_client = docker.from_env()
    docker_client.containers.get(name).stop()