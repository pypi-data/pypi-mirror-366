import logging
from pathlib import Path
from typing import Optional, Tuple

import paramiko

from ..config import Config


class SSHClient:
    """SSH client for connecting to and executing commands on a remote cluster."""

    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[paramiko.SSHClient] = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Connect to the SSH server.
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connection parameters
            connect_kwargs = {
                "hostname": self.config.hostname,
                "port": self.config.port,
                "username": self.config.username,
                "timeout": 30,
            }

            # Use specific private key if provided
            if self.config.private_key_path:
                private_key_path = Path(self.config.private_key_path).expanduser()
                if private_key_path.exists():
                    connect_kwargs["key_filename"] = str(private_key_path)
                else:
                    self.logger.warning(f"Private key not found: {private_key_path}")

            print("connect_kwargs", connect_kwargs)
            self.client.connect(**connect_kwargs)
            print("connected", connect_kwargs)
            return True

        except Exception as e:
            print(f"Failed to connect to SSH server: {e}")
            if self.client:
                self.client.close()
                self.client = None
            return False

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on the remote server.

        Args:
            command: Command to execute

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            raise RuntimeError("SSH client not connected. Call connect() first.")

        try:
            self.logger.debug(f"Executing command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode("utf-8")
            stderr_data = stderr.read().decode("utf-8")

            self.logger.debug(f"Command exit code: {exit_code}")
            if stderr_data:
                self.logger.warning(f"Command stderr: {stderr_data}")

            return exit_code, stdout_data, stderr_data

        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}': {e}")
            raise

    def is_connected(self) -> bool:
        """Check if SSH connection is active."""
        return self.client is not None and self.client.get_transport() is not None

    def disconnect(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.logger.info("SSH connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
