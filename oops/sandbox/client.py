"""Docker sandbox client for Oops.

This module provides a client to interact with the Docker sandbox container,
checking its status and managing its lifecycle.
"""

import os
import docker
from docker.errors import DockerException, NotFound, APIError
from typing import Optional, Dict, Any


class SandboxClient:
    """Client for managing the Docker sandbox container."""
    
    def __init__(
        self,
        container_name: Optional[str] = None,
        image_name: Optional[str] = None,
        auto_start: bool = True
    ):
        """Initialize the sandbox client.
        
        Args:
            container_name: Name of the sandbox container
            image_name: Name of the sandbox image
            auto_start: Whether to auto-start the sandbox if not running
        """
        self.container_name = container_name or os.getenv(
            "SANDBOX_CONTAINER_NAME", "oops-tools-sandbox"
        )
        self.image_name = image_name or os.getenv(
            "SANDBOX_IMAGE", "oops-tools:latest"
        )
        self.auto_start = auto_start and os.getenv(
            "SANDBOX_AUTO_START", "true"
        ).lower() == "true"
        
        try:
            self.client = docker.from_env()
        except DockerException as e:
            self.client = None
            self._docker_error = str(e)
    
    def is_available(self) -> bool:
        """Check if Docker is available on the system.
        
        Returns:
            True if Docker is available, False otherwise
        """
        return self.client is not None
    
    def is_running(self) -> bool:
        """Check if the sandbox container is running.
        
        Returns:
            True if container is running, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            container = self.client.containers.get(self.container_name)
            return container.status == "running"
        except NotFound:
            return False
        except APIError:
            return False
    
    def start(self) -> bool:
        """Start the sandbox container.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            # Try to get existing container
            container = self.client.containers.get(self.container_name)
            
            if container.status != "running":
                container.start()
                return True
            return True
            
        except NotFound:
            # Container doesn't exist, create it
            try:
                self.client.containers.run(
                    self.image_name,
                    name=self.container_name,
                    detach=True,
                    remove=False,
                    network_mode="bridge",
                    cap_add=["NET_RAW", "NET_ADMIN"],
                    cap_drop=["ALL"],
                    security_opt=["no-new-privileges:true"],
                    volumes={
                        os.path.abspath("./output"): {
                            "bind": "/output",
                            "mode": "rw"
                        }
                    }
                )
                return True
            except APIError as e:
                print(f"Failed to create container: {e}")
                return False
        except APIError as e:
            print(f"Failed to start container: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the sandbox container.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            container = self.client.containers.get(self.container_name)
            container.stop()
            return True
        except (NotFound, APIError):
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of the sandbox.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "docker_available": self.is_available(),
            "container_running": False,
            "container_status": None,
            "image_available": False,
        }
        
        if not self.is_available():
            status["error"] = getattr(self, "_docker_error", "Docker not available")
            return status
        
        # Check if image exists
        try:
            self.client.images.get(self.image_name)
            status["image_available"] = True
        except NotFound:
            status["image_available"] = False
        
        # Check container status
        try:
            container = self.client.containers.get(self.container_name)
            status["container_running"] = container.status == "running"
            status["container_status"] = container.status
        except NotFound:
            status["container_status"] = "not_found"
        
        return status
    
    def ensure_running(self) -> bool:
        """Ensure the sandbox is running, starting it if necessary.
        
        Returns:
            True if sandbox is running, False otherwise
        """
        if self.is_running():
            return True
        
        if self.auto_start:
            return self.start()
        
        return False
