import json
from typing import Dict, List, Optional

from ..ssh.cluster import SSHClient
from .types import CondorJob


class HTCondorClient:
    """Client for interacting with HTCondor through SSH."""

    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    def get_user_jobs(self, username: str) -> List[CondorJob]:
        """
        Get all jobs for a specific user.

        Args:
            username: Username to query jobs for

        Returns:
            List of CondorJob objects

        Raises:
            RuntimeError: If command execution fails or returns invalid data
        """
        command = f"condor_q {username} -json"

        try:
            exit_code, stdout, stderr = self.ssh_client.execute_command(command)

            if exit_code != 0:
                error_msg = f"condor_q command failed (exit code {exit_code}): {stderr}"
                print(error_msg)
                raise RuntimeError(error_msg)

            if not stdout.strip():
                print(f"No jobs found for user {username}")
                return []

            # Parse JSON output
            try:
                job_data = json.loads(stdout)
                jobs = []

                # HTCondor JSON format can be a list of jobs or empty
                if isinstance(job_data, list):
                    for job_dict in job_data:
                        try:
                            job = CondorJob.from_dict(job_dict)
                            jobs.append(job)
                        except Exception as e:
                            print(f"Failed to parse job data: {e}")
                            continue

                print(f"Retrieved {len(jobs)} jobs for user {username}")
                return jobs

            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse condor_q JSON output: {e}"
                print(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            print(f"Failed to retrieve jobs for user {username}: {e}")
            raise

    def get_job_status_summary(self, username: str) -> Dict[str, int]:
        """
        Get a summary of job statuses for a user.

        Args:
            username: Username to query jobs for

        Returns:
            Dictionary with status names as keys and counts as values
        """
        jobs = self.get_user_jobs(username)
        summary = {}

        for job in jobs:
            status = job.job_status_name
            summary[status] = summary.get(status, 0) + 1

        return summary

    def get_job_logs(self, job_id: str) -> Optional[str]:
        """
        Get log file content for a specific job (placeholder for future implementation).

        Args:
            job_id: Job ID in format "cluster.proc"

        Returns:
            Log content if available, None otherwise
        """
        # This is a placeholder - actual implementation would depend on
        # HTCondor configuration and log file locations
        print(f"Log retrieval not yet implemented for job {job_id}")
        return None

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a HTCondor job using condor_rm.

        Args:
            job_id: Job ID in format "cluster.proc" or just "cluster"

        Returns:
            True if job was successfully canceled, False otherwise

        Raises:
            RuntimeError: If command execution fails
        """
        command = f"condor_rm {job_id}"

        try:
            exit_code, stdout, stderr = self.ssh_client.execute_command(command)

            if exit_code == 0:
                print(f"Successfully canceled job {job_id}")
                print(f"condor_rm output: {stdout}")
                return True
            else:
                error_msg = (
                    f"condor_rm command failed (exit code {exit_code}): {stderr}"
                )
                print(error_msg)
                return False

        except Exception as e:
            error_msg = f"Failed to cancel job {job_id}: {e}"
            print(error_msg)
            raise RuntimeError(error_msg)

    def ssh_to_job(self, job: CondorJob) -> None:
        """
        Open a separate terminal with SSH connection to the execution node where a job is running,
        using HTCondor's condor_ssh_to_job command on the login node.

        Args:
            job: CondorJob object containing job information

        Raises:
            RuntimeError: If job is not running or SSH connection setup fails
        """
        import subprocess
        import shlex

        # Check if job is running
        if not job.is_running:
            raise RuntimeError(
                f"Job {job.job_id} is not running (status: {job.job_status_name})"
            )

        # Extract cluster ID from job_id (format is "cluster.proc")
        cluster_id = job.job_id.split(".")[0]

        print(f"Opening terminal with condor_ssh_to_job for cluster {cluster_id}")

        try:
            # Get the login node config
            login_config = self.ssh_client.config

            # Build SSH command to login node with condor_ssh_to_job
            ssh_command_parts = ["ssh"]

            # Add private key if specified
            if login_config.private_key_path:
                ssh_command_parts.extend(["-i", login_config.private_key_path])

            # Add port if non-standard
            if login_config.port != 22:
                ssh_command_parts.extend(["-p", str(login_config.port)])

            # Add login node and the condor_ssh_to_job command
            login_node = f"{login_config.username}@{login_config.hostname}"
            ssh_command_parts.extend(
                ["-t", login_node, f"condor_ssh_to_job {cluster_id}"]
            )

            ssh_command = " ".join(shlex.quote(part) for part in ssh_command_parts)

            # Open terminal with SSH + condor_ssh_to_job command (macOS)
            terminal_command = [
                "osascript",
                "-e",
                f'tell application "Terminal" to do script "{ssh_command}"',
            ]

            print(f"Executing: {' '.join(terminal_command)}")
            subprocess.run(terminal_command, check=True)

            print(
                f"✓ Opened terminal with condor_ssh_to_job {cluster_id} on login node {login_config.hostname}"
            )

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to open terminal with condor_ssh_to_job: {e}"
            print(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to setup condor_ssh_to_job connection for cluster {cluster_id}: {e}"
            print(error_msg)
            raise RuntimeError(error_msg)
