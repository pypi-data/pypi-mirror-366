"""
Simple Docker client exposure helpers.
Demonstrates different ways to expose Docker functionality in yaapp.
"""

import docker
from yaapp import yaapp


def expose_docker_client_simple():
    """
    Simplest approach: expose the Docker client as a single object.
    
    Usage:
        from yaapp.plugins.docker.simple_exposure import expose_docker_client_simple
        expose_docker_client_simple()
        
        # Then you can call:
        # app.execute_function("docker.ping")
        # app.execute_function("docker.version")
    """
    try:
        client = docker.from_env()
        yaapp.expose(client, name="docker")
        print("✅ Docker client exposed as 'docker'")
        return True
    except Exception as e:
        print(f"❌ Failed to expose Docker client: {e}")
        return False


def expose_docker_methods_individually():
    """
    Expose individual Docker methods for direct CLI access.
    
    This creates individual commands like:
    - docker_ping
    - docker_version
    - docker_list_containers
    - etc.
    """
    try:
        client = docker.from_env()
        
        # System methods
        yaapp.expose(client.ping, name="docker_ping")
        yaapp.expose(client.version, name="docker_version")
        yaapp.expose(client.info, name="docker_info")
        
        # Container methods
        yaapp.expose(client.containers.list, name="docker_list_containers")
        yaapp.expose(client.containers.get, name="docker_get_container")
        yaapp.expose(client.containers.run, name="docker_run_container")
        
        # Image methods
        yaapp.expose(client.images.list, name="docker_list_images")
        yaapp.expose(client.images.pull, name="docker_pull_image")
        yaapp.expose(client.images.get, name="docker_get_image")
        
        # Volume methods
        yaapp.expose(client.volumes.list, name="docker_list_volumes")
        yaapp.expose(client.volumes.create, name="docker_create_volume")
        yaapp.expose(client.volumes.get, name="docker_get_volume")
        
        # Network methods
        yaapp.expose(client.networks.list, name="docker_list_networks")
        yaapp.expose(client.networks.create, name="docker_create_network")
        yaapp.expose(client.networks.get, name="docker_get_network")
        
        print("✅ Docker methods exposed individually")
        return True
        
    except Exception as e:
        print(f"❌ Failed to expose Docker methods: {e}")
        return False


class SimpleDockerWrapper:
    """
    Simple wrapper that exposes Docker functionality with clean method names.
    
    Usage:
        wrapper = SimpleDockerWrapper()
        yaapp.expose(wrapper, name="docker")
    """
    
    def __init__(self):
        """Initialize Docker client."""
        self.client = docker.from_env()
    
    # System methods
    def ping(self):
        """Ping Docker daemon."""
        return self.client.ping()
    
    def version(self):
        """Get Docker version."""
        return self.client.version()
    
    def info(self):
        """Get Docker system info."""
        return self.client.info()
    
    # Container methods
    def list_containers(self, all: bool = False):
        """List containers."""
        containers = self.client.containers.list(all=all)
        return [
            {
                "id": c.id[:12],
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else c.image.id[:12]
            }
            for c in containers
        ]
    
    def get_container(self, container_id: str):
        """Get container by ID or name."""
        container = self.client.containers.get(container_id)
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else container.image.id,
            "created": container.attrs.get("Created", ""),
            "ports": container.ports
        }
    
    def start_container(self, container_id: str):
        """Start a container."""
        container = self.client.containers.get(container_id)
        container.start()
        return f"Started container {container.name}"
    
    def stop_container(self, container_id: str):
        """Stop a container."""
        container = self.client.containers.get(container_id)
        container.stop()
        return f"Stopped container {container.name}"
    
    def remove_container(self, container_id: str, force: bool = False):
        """Remove a container."""
        container = self.client.containers.get(container_id)
        container.remove(force=force)
        return f"Removed container {container.name}"
    
    def run_container(self, image: str, command: str = None, name: str = None, detach: bool = True):
        """Run a new container."""
        container = self.client.containers.run(
            image=image,
            command=command,
            name=name,
            detach=detach
        )
        
        if detach:
            return {
                "id": container.id[:12],
                "name": container.name,
                "status": container.status
            }
        else:
            return container.decode('utf-8') if isinstance(container, bytes) else str(container)
    
    # Image methods
    def list_images(self):
        """List images."""
        images = self.client.images.list()
        return [
            {
                "id": img.id[:12],
                "tags": img.tags,
                "size": img.attrs.get("Size", 0)
            }
            for img in images
        ]
    
    def pull_image(self, repository: str, tag: str = "latest"):
        """Pull an image."""
        image = self.client.images.pull(repository, tag=tag)
        return {
            "id": image.id[:12],
            "tags": image.tags,
            "size": image.attrs.get("Size", 0)
        }
    
    def remove_image(self, image_id: str, force: bool = False):
        """Remove an image."""
        self.client.images.remove(image_id, force=force)
        return f"Removed image {image_id}"
    
    # Volume methods
    def list_volumes(self):
        """List volumes."""
        volumes = self.client.volumes.list()
        return [
            {
                "name": vol.name,
                "driver": vol.attrs.get("Driver", ""),
                "mountpoint": vol.attrs.get("Mountpoint", "")
            }
            for vol in volumes
        ]
    
    def create_volume(self, name: str):
        """Create a volume."""
        volume = self.client.volumes.create(name=name)
        return {
            "name": volume.name,
            "driver": volume.attrs.get("Driver", ""),
            "mountpoint": volume.attrs.get("Mountpoint", "")
        }
    
    def remove_volume(self, name: str):
        """Remove a volume."""
        volume = self.client.volumes.get(name)
        volume.remove()
        return f"Removed volume {name}"


def expose_simple_docker_wrapper():
    """
    Expose the simple Docker wrapper.
    
    This provides a clean interface with organized methods under 'docker' namespace.
    """
    try:
        wrapper = SimpleDockerWrapper()
        yaapp.expose(wrapper, name="docker")
        print("✅ Simple Docker wrapper exposed as 'docker'")
        return True
    except Exception as e:
        print(f"❌ Failed to expose Docker wrapper: {e}")
        return False


# Auto-expose the simple wrapper when this module is imported
if __name__ != "__main__":
    # Only auto-expose if not running as main script
    try:
        expose_simple_docker_wrapper()
    except Exception:
        pass  # Fail silently if Docker is not available