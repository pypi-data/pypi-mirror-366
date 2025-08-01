from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class CondorJob:
    """Represents a single HTCondor job with comprehensive field mapping."""

    # Core job identification
    cluster_id: int
    proc_id: int
    global_job_id: str

    # Job status and lifecycle
    job_status: int
    job_status_name: str
    last_job_status: Optional[int]

    # User and ownership
    owner: str
    user: str
    accounting_group: Optional[str]

    # Command and execution
    cmd: str
    args: str
    executable_size: Optional[int]

    # Timing information
    q_date: Optional[datetime]  # Submission time
    job_start_date: Optional[datetime]
    job_current_start_date: Optional[datetime]
    job_current_start_executing_date: Optional[datetime]
    entered_current_status: Optional[datetime]

    # Resource requests and usage
    request_cpus: Optional[int]
    request_memory: Optional[int]
    request_disk: Optional[str]
    request_gpus: Optional[int]

    # Resource provisioning and usage
    cpus_provisioned: Optional[int]
    memory_provisioned: Optional[int]
    disk_provisioned: Optional[int]
    gpus_provisioned: Optional[int]

    # GPU information
    assigned_gpus: Optional[str]

    # CPU and memory usage
    cpus_usage: Optional[float]
    memory_usage: Optional[str]
    resident_set_size: Optional[int]

    # CPU time statistics
    remote_user_cpu: Optional[float]
    remote_sys_cpu: Optional[float]
    cumulative_remote_user_cpu: Optional[float]
    cumulative_remote_sys_cpu: Optional[float]

    # Execution environment
    remote_host: Optional[str]
    file_system_domain: Optional[str]
    iwd: Optional[str]  # Initial working directory

    # I/O files
    input_file: Optional[str]
    output_file: Optional[str]
    error_file: Optional[str]
    user_log: Optional[str]

    # Job policy and requirements
    requirements: Optional[str]
    rank: Optional[float]
    on_exit_hold: Optional[bool]
    on_exit_remove: Optional[bool]
    periodic_remove: Optional[str]

    # Transfer settings
    should_transfer_files: Optional[str]
    when_to_transfer_output: Optional[str]
    transfer_input_size_mb: Optional[int]

    # Condor version and platform
    condor_version: Optional[str]
    condor_platform: Optional[str]

    # Job priority and universe
    job_prio: Optional[int]
    job_universe: Optional[int]

    # Run statistics
    job_run_count: Optional[int]
    num_job_starts: Optional[int]
    num_job_matches: Optional[int]
    num_restarts: Optional[int]

    @classmethod
    def from_dict(cls, job_data: Dict[str, Any]) -> "CondorJob":
        """Create a CondorJob from HTCondor JSON data."""
        # HTCondor job status mapping
        status_map = {
            0: "Unexpanded",
            1: "Idle",
            2: "Running",
            3: "Removed",
            4: "Completed",
            5: "Held",
            6: "Transferring Output",
            7: "Suspended",
        }

        def parse_timestamp(timestamp: Optional[int]) -> Optional[datetime]:
            """Parse Unix timestamp to datetime."""
            if timestamp is None:
                return None
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                return None

        return cls(
            # Core identification
            cluster_id=job_data.get("ClusterId", 0),
            proc_id=job_data.get("ProcId", 0),
            global_job_id=job_data.get("GlobalJobId", ""),
            # Status
            job_status=job_data.get("JobStatus", 0),
            job_status_name=status_map.get(job_data.get("JobStatus", 0), "Unknown"),
            last_job_status=job_data.get("LastJobStatus"),
            # User info
            owner=job_data.get("Owner", ""),
            user=job_data.get("User", ""),
            accounting_group=job_data.get("AccountingGroup"),
            # Command
            cmd=job_data.get("Cmd", ""),
            args=job_data.get("Args", ""),
            executable_size=job_data.get("ExecutableSize"),
            # Timing
            q_date=parse_timestamp(job_data.get("QDate")),
            job_start_date=parse_timestamp(job_data.get("JobStartDate")),
            job_current_start_date=parse_timestamp(job_data.get("JobCurrentStartDate")),
            job_current_start_executing_date=parse_timestamp(
                job_data.get("JobCurrentStartExecutingDate")
            ),
            entered_current_status=parse_timestamp(
                job_data.get("EnteredCurrentStatus")
            ),
            # Resource requests
            request_cpus=job_data.get("RequestCpus"),
            request_memory=job_data.get("RequestMemory"),
            request_disk=job_data.get("RequestDisk"),
            request_gpus=job_data.get("RequestGPUs"),
            # Resource provisioning
            cpus_provisioned=job_data.get("CpusProvisioned"),
            memory_provisioned=job_data.get("MemoryProvisioned"),
            disk_provisioned=job_data.get("DiskProvisioned"),
            gpus_provisioned=job_data.get("GPUsProvisioned"),
            # GPU info
            assigned_gpus=job_data.get("AssignedGPUs"),
            # Usage
            cpus_usage=job_data.get("CpusUsage"),
            memory_usage=job_data.get("MemoryUsage"),
            resident_set_size=job_data.get("ResidentSetSize"),
            # CPU time
            remote_user_cpu=job_data.get("RemoteUserCpu"),
            remote_sys_cpu=job_data.get("RemoteSysCpu"),
            cumulative_remote_user_cpu=job_data.get("CumulativeRemoteUserCpu"),
            cumulative_remote_sys_cpu=job_data.get("CumulativeRemoteSysCpu"),
            # Execution environment
            remote_host=job_data.get("RemoteHost"),
            file_system_domain=job_data.get("FileSystemDomain"),
            iwd=job_data.get("Iwd"),
            # I/O files
            input_file=job_data.get("In"),
            output_file=job_data.get("Out"),
            error_file=job_data.get("Err"),
            user_log=job_data.get("UserLog"),
            # Job policy
            requirements=job_data.get("Requirements"),
            rank=job_data.get("Rank"),
            on_exit_hold=job_data.get("OnExitHold"),
            on_exit_remove=job_data.get("OnExitRemove"),
            periodic_remove=job_data.get("PeriodicRemove"),
            # Transfer
            should_transfer_files=job_data.get("ShouldTransferFiles"),
            when_to_transfer_output=job_data.get("WhenToTransferOutput"),
            transfer_input_size_mb=job_data.get("TransferInputSizeMB"),
            # Platform info
            condor_version=job_data.get("CondorVersion"),
            condor_platform=job_data.get("CondorPlatform"),
            # Priority and universe
            job_prio=job_data.get("JobPrio"),
            job_universe=job_data.get("JobUniverse"),
            # Run stats
            job_run_count=job_data.get("JobRunCount"),
            num_job_starts=job_data.get("NumJobStarts"),
            num_job_matches=job_data.get("NumJobMatches"),
            num_restarts=job_data.get("NumRestarts"),
        )

    @property
    def job_id(self) -> str:
        """Get the full job ID (cluster.proc)."""
        return f"{self.cluster_id}.{self.proc_id}"

    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.job_status == 2

    @property
    def is_idle(self) -> bool:
        """Check if job is idle/waiting."""
        return self.job_status == 1

    @property
    def is_completed(self) -> bool:
        """Check if job has completed."""
        return self.job_status == 4

    @property
    def is_held(self) -> bool:
        """Check if job is held."""
        return self.job_status == 5

    @property
    def runtime_seconds(self) -> Optional[int]:
        """Calculate runtime in seconds if job is running."""
        if self.job_current_start_executing_date and self.is_running:
            return int(
                (datetime.now() - self.job_current_start_executing_date).total_seconds()
            )
        return None


# Legacy alias for backward compatibility
Job = CondorJob
