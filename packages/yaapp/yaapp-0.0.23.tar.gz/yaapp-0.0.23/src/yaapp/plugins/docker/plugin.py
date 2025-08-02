"""
Docker plugin for yaapp framework.
Provides Docker container and image management through the Docker Python client.
"""

import asyncio
import docker
from typing import Dict, List, Any, Optional
from yaapp import yaapp
from yaapp.result import Result, Ok


@yaapp.expose("docker")
class Docker:
    """Docker plugin that exposes Docker client functionality."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Docker plugin with configuration."""
        self.config = config or {}
        self.yaapp = None  # Will be set by the main app when registered
        
        # Initialize Docker client
        try:
            # Try to connect to Docker daemon
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            print("✅ Docker: Connected to Docker daemon")
        except Exception as e:
            print(f"❌ Docker: Failed to connect to Docker daemon: {e}")
            self.client = None
    
    def _ensure_client(self) -> bool:
        """Ensure Docker client is available."""
        if self.client is None:
            try:
                self.client = docker.from_env()
                self.client.ping()
                return True
            except Exception:
                return False
        return True
    
    # Container Management
    async def list_containers(self, all: bool = False) -> Result[List[Dict[str, Any]]]:
        """List Docker containers."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            containers = await asyncio.to_thread(self.client.containers.list, all=all)
            container_info = []
            for container in containers:
                container_info.append({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else container.image.id,
                    "created": container.attrs.get("Created", ""),
                    "ports": container.ports
                })
            return Ok(container_info)
        except Exception as e:
            return Result.error(f"Failed to list containers: {str(e)}")
    
    async def get_container(self, container_id: str) -> Result[Dict[str, Any]]:
        """Get detailed information about a specific container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.get(container_id)
            return Ok({
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "created": container.attrs.get("Created", ""),
                "ports": container.ports,
                "labels": container.labels,
                "env": container.attrs.get("Config", {}).get("Env", []),
                "mounts": [mount for mount in container.attrs.get("Mounts", [])]
            })
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to get container: {str(e)}")
    
    async def start_container(self, container_id: str) -> Result[bool]:
        """Start a Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = await asyncio.to_thread(self.client.containers.get, container_id)
            await asyncio.to_thread(container.start)
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to start container: {str(e)}")
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> Result[bool]:
        """Stop a Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to stop container: {str(e)}")
    
    async def restart_container(self, container_id: str, timeout: int = 10) -> Result[bool]:
        """Restart a Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to restart container: {str(e)}")
    
    async def remove_container(self, container_id: str, force: bool = False) -> Result[bool]:
        """Remove a Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to remove container: {str(e)}")
    
    async def run_container(self, image: str, command: str = None, name: str = None, 
                     detach: bool = True, ports: Dict[str, int] = None,
                     environment: Dict[str, str] = None, volumes: Dict[str, Dict[str, str]] = None) -> Result[Dict[str, Any]]:
        """Run a new Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.run(
                image=image,
                command=command,
                name=name,
                detach=detach,
                ports=ports,
                environment=environment,
                volumes=volumes
            )
            
            if detach:
                return Ok({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status
                })
            else:
                # If not detached, return the output
                return Ok({
                    "output": container.decode('utf-8') if isinstance(container, bytes) else str(container)
                })
        except Exception as e:
            return Result.error(f"Failed to run container: {str(e)}")
    
    async def get_container_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> Result[str]:
        """Get logs from a Docker container."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, follow=follow)
            return Ok(logs.decode('utf-8') if isinstance(logs, bytes) else str(logs))
        except docker.errors.NotFound:
            return Result.error(f"Container '{container_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to get container logs: {str(e)}")
    
    # Image Management
    async def list_images(self, all: bool = False) -> Result[List[Dict[str, Any]]]:
        """List Docker images."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            images = self.client.images.list(all=all)
            image_info = []
            for image in images:
                image_info.append({
                    "id": image.id,
                    "tags": image.tags,
                    "created": image.attrs.get("Created", ""),
                    "size": image.attrs.get("Size", 0),
                    "labels": image.labels or {}
                })
            return Ok(image_info)
        except Exception as e:
            return Result.error(f"Failed to list images: {str(e)}")
    
    async def pull_image(self, repository: str, tag: str = "latest") -> Result[Dict[str, Any]]:
        """Pull a Docker image from registry."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            image = self.client.images.pull(repository, tag=tag)
            return Ok({
                "id": image.id,
                "tags": image.tags,
                "size": image.attrs.get("Size", 0)
            })
        except Exception as e:
            return Result.error(f"Failed to pull image: {str(e)}")
    
    async def remove_image(self, image_id: str, force: bool = False) -> Result[bool]:
        """Remove a Docker image."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            self.client.images.remove(image_id, force=force)
            return Ok(True)
        except docker.errors.ImageNotFound:
            return Result.error(f"Image '{image_id}' not found")
        except Exception as e:
            return Result.error(f"Failed to remove image: {str(e)}")
    
    async def build_image(self, path: str, tag: str = None, dockerfile: str = "Dockerfile") -> Result[Dict[str, Any]]:
        """Build a Docker image from a Dockerfile."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            image, build_logs = self.client.images.build(
                path=path,
                tag=tag,
                dockerfile=dockerfile
            )
            
            # Collect build logs
            logs = []
            for log in build_logs:
                if 'stream' in log:
                    logs.append(log['stream'].strip())
            
            return Ok({
                "id": image.id,
                "tags": image.tags,
                "build_logs": logs
            })
        except Exception as e:
            return Result.error(f"Failed to build image: {str(e)}")
    
    # System Information
    async def get_system_info(self) -> Result[Dict[str, Any]]:
        """Get Docker system information."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            info = await asyncio.to_thread(self.client.info)
            return Ok({
                "containers": info.get("Containers", 0),
                "containers_running": info.get("ContainersRunning", 0),
                "containers_paused": info.get("ContainersPaused", 0),
                "containers_stopped": info.get("ContainersStopped", 0),
                "images": info.get("Images", 0),
                "server_version": info.get("ServerVersion", ""),
                "kernel_version": info.get("KernelVersion", ""),
                "operating_system": info.get("OperatingSystem", ""),
                "architecture": info.get("Architecture", ""),
                "memory_total": info.get("MemTotal", 0),
                "cpus": info.get("NCPU", 0)
            })
        except Exception as e:
            return Result.error(f"Failed to get system info: {str(e)}")
    
    async def get_version(self) -> Result[Dict[str, Any]]:
        """Get Docker version information."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            version = await asyncio.to_thread(self.client.version)
            return Ok(version)
        except Exception as e:
            return Result.error(f"Failed to get version: {str(e)}")
    
    async def ping(self) -> Result[bool]:
        """Ping Docker daemon to check connectivity."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            await asyncio.to_thread(self.client.ping)
            return Ok(True)
        except Exception as e:
            return Result.error(f"Docker daemon not responding: {str(e)}")
    
    # Volume Management
    def list_volumes(self) -> Result[List[Dict[str, Any]]]:
        """List Docker volumes."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            volumes = self.client.volumes.list()
            volume_info = []
            for volume in volumes:
                volume_info.append({
                    "name": volume.name,
                    "driver": volume.attrs.get("Driver", ""),
                    "mountpoint": volume.attrs.get("Mountpoint", ""),
                    "created": volume.attrs.get("CreatedAt", ""),
                    "labels": volume.attrs.get("Labels") or {}
                })
            return Ok(volume_info)
        except Exception as e:
            return Result.error(f"Failed to list volumes: {str(e)}")
    
    async def create_volume(self, name: str, driver: str = "local", labels: Dict[str, str] = None) -> Result[Dict[str, Any]]:
        """Create a Docker volume."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            volume = self.client.volumes.create(name=name, driver=driver, labels=labels)
            return Ok({
                "name": volume.name,
                "driver": volume.attrs.get("Driver", ""),
                "mountpoint": volume.attrs.get("Mountpoint", "")
            })
        except Exception as e:
            return Result.error(f"Failed to create volume: {str(e)}")
    
    async def remove_volume(self, name: str, force: bool = False) -> Result[bool]:
        """Remove a Docker volume."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            volume = self.client.volumes.get(name)
            volume.remove(force=force)
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Volume '{name}' not found")
        except Exception as e:
            return Result.error(f"Failed to remove volume: {str(e)}")
    
    # Network Management
    def list_networks(self) -> Result[List[Dict[str, Any]]]:
        """List Docker networks."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            networks = self.client.networks.list()
            network_info = []
            for network in networks:
                network_info.append({
                    "id": network.id,
                    "name": network.name,
                    "driver": network.attrs.get("Driver", ""),
                    "scope": network.attrs.get("Scope", ""),
                    "created": network.attrs.get("Created", ""),
                    "labels": network.attrs.get("Labels") or {}
                })
            return Ok(network_info)
        except Exception as e:
            return Result.error(f"Failed to list networks: {str(e)}")
    
    async def create_network(self, name: str, driver: str = "bridge", labels: Dict[str, str] = None) -> Result[Dict[str, Any]]:
        """Create a Docker network."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            network = self.client.networks.create(name=name, driver=driver, labels=labels)
            return Ok({
                "id": network.id,
                "name": network.name,
                "driver": network.attrs.get("Driver", "")
            })
        except Exception as e:
            return Result.error(f"Failed to create network: {str(e)}")
    
    async def remove_network(self, name: str) -> Result[bool]:
        """Remove a Docker network."""
        if not self._ensure_client():
            return Result.error("Docker daemon not available")
        
        try:
            network = self.client.networks.get(name)
            network.remove()
            return Ok(True)
        except docker.errors.NotFound:
            return Result.error(f"Network '{name}' not found")
        except Exception as e:
            return Result.error(f"Failed to remove network: {str(e)}")