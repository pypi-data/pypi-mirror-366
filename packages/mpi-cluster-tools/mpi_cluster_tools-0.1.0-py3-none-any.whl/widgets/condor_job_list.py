"""Widget for displaying HTCondor jobs in a list format."""

from datetime import datetime
from typing import List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static

from ..htcondor.types import CondorJob


class CondorJobItem(ListItem):
    """A single job item in the job list."""

    def __init__(self, job: CondorJob, *args, **kwargs):
        # Add focus-container class
        if "classes" in kwargs:
            kwargs["classes"] = f"{kwargs['classes']} focus-container".strip()
        else:
            kwargs["classes"] = "focus-container"
        super().__init__(*args, **kwargs)
        self.job = job
        self.border_title = self.job.job_id

    def compose(self) -> ComposeResult:
        """Compose the job item layout."""
        with Vertical(classes="job-item"):
            with Horizontal(classes="job-line-1"):
                yield Static(self._get_status_indicator(), classes="status-indicator")
                yield Static(self._get_main_info(), classes="job-main-info")
            with Horizontal(classes="job-line-2"):
                yield Static(self._get_resource_info(), classes="job-resource-info")

    def _get_status_indicator(self) -> Text:
        """Get status with colored dot indicator."""
        status_colors = {
            "Running": "green",
            "Idle": "yellow",
            "Completed": "blue",
            "Held": "red",
            "Removed": "red",
            "Transferring Output": "cyan",
            "Suspended": "orange",
            "Unexpanded": "gray",
        }

        color = status_colors.get(self.job.job_status_name, "white")
        text = Text()
        text.append("● ", style=color)
        text.append(self.job.job_status_name, style="bold")
        return text

    def _get_main_info(self) -> str:
        """Get main job information for first line."""
        hostname = self._extract_hostname(self.job.remote_host)
        job_id = self.job.global_job_id or self.job.job_id

        # Truncate long job IDs for display
        if len(job_id) > 40:
            job_id = job_id[:37] + "..."

        return f"{hostname}: {job_id}"

    def _get_resource_info(self) -> str:
        """Get resource and runtime information for second line."""
        parts = []

        # Runtime information
        runtime = self._get_runtime_display()
        if runtime:
            parts.append(f"Runtime: {runtime}")

        # CPU information
        if self.job.request_cpus:
            cpu_usage = ""
            if self.job.cpus_usage is not None:
                cpu_usage = f" ({self.job.cpus_usage:.1%} used)"
            parts.append(f"CPUs: {self.job.request_cpus}{cpu_usage}")

        # Memory information
        if self.job.request_memory:
            memory_gb = self.job.request_memory / 1024
            memory_usage = ""
            if self.job.resident_set_size:
                used_gb = self.job.resident_set_size / (1024 * 1024)
                memory_usage = f" ({used_gb:.1f}GB used)"
            parts.append(f"Mem: {memory_gb:.1f}GB{memory_usage}")

        # GPU information
        if self.job.request_gpus:
            gpu_info = f"GPUs: {self.job.request_gpus}"
            if self.job.assigned_gpus:
                # Extract GPU model from assigned GPU string
                gpu_model = self._extract_gpu_model(self.job.assigned_gpus)
                if gpu_model:
                    gpu_info += f" ({gpu_model})"
            parts.append(gpu_info)

        print(parts)
        return " | ".join(parts)

    def _extract_hostname(self, remote_host: Optional[str]) -> str:
        """Extract hostname from remote host string."""
        if not remote_host:
            return "unknown"

        # HTCondor remote host format: slot1_3@g057.internal.cluster.is.localnet
        if "@" in remote_host:
            hostname = remote_host.split("@")[1]
            # Remove domain suffix for cleaner display
            if "." in hostname:
                hostname = hostname.split(".")[0]
            return hostname

        return remote_host

    def _extract_gpu_model(self, assigned_gpus: str) -> Optional[str]:
        """Extract GPU model from assigned GPU string."""
        # Simple extraction - in practice this might need more sophisticated parsing
        # Example: "GPU-d35a3099" -> "GPU-d35a3099"
        if assigned_gpus and len(assigned_gpus) > 10:
            return assigned_gpus[:10] + "..."
        return assigned_gpus

    def _get_runtime_display(self) -> Optional[str]:
        """Get formatted runtime display."""
        if self.job.is_running and self.job.job_current_start_executing_date:
            # Calculate current runtime
            runtime_seconds = (
                datetime.now() - self.job.job_current_start_executing_date
            ).total_seconds()
            return self._format_duration(int(runtime_seconds))
        elif self.job.remote_user_cpu and self.job.remote_sys_cpu:
            # Use CPU time for completed jobs
            total_cpu_time = self.job.remote_user_cpu + self.job.remote_sys_cpu
            return f"{self._format_duration(int(total_cpu_time))} (CPU)"
        elif self.job.cumulative_remote_user_cpu and self.job.cumulative_remote_sys_cpu:
            # Use cumulative CPU time
            total_cpu_time = (
                self.job.cumulative_remote_user_cpu + self.job.cumulative_remote_sys_cpu
            )
            return f"{self._format_duration(int(total_cpu_time))} (CPU)"

        return None

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"


class CondorJobList(Widget):
    """Widget for displaying a list of HTCondor jobs."""

    jobs: reactive[List[CondorJob]] = reactive([])
    selected_job: reactive[Optional[CondorJob]] = reactive(None)

    def __init__(self, jobs: Optional[List[CondorJob]] = None, *args, **kwargs):
        # Add focus-container class
        if "classes" in kwargs:
            kwargs["classes"] = f"{kwargs['classes']} focus-container".strip()
        else:
            kwargs["classes"] = "focus-container"
        super().__init__(*args, **kwargs)
        if jobs:
            self.jobs = jobs

    def compose(self) -> ComposeResult:
        """Compose the job list widget."""
        with Vertical(classes="condor-job-list"):
            yield Static("My Jobs", classes="job-list-header")
            yield ListView(id="job-list", classes="focus-container")

    def on_mount(self) -> None:
        """Set up the widget when mounted."""
        self._refresh_job_list()

    def watch_jobs(self, jobs: List[CondorJob]) -> None:
        """React to changes in the jobs list."""
        self._refresh_job_list()

    def _refresh_job_list(self) -> None:
        """Refresh the job list display."""
        job_list = self.query_one("#job-list", ListView)
        job_list.clear()

        if not self.jobs:
            job_list.append(ListItem(Static("No jobs found", classes="no-jobs")))
            return

        # Sort jobs by status priority and submission time
        sorted_jobs = sorted(
            self.jobs,
            key=lambda job: (
                self._get_status_priority(job.job_status),
                -(job.q_date.timestamp() if job.q_date else 0),
            ),
        )

        for job in sorted_jobs:
            job_list.append(CondorJobItem(job))

        # Select the first job by default if we have jobs
        if sorted_jobs:
            job_list.index = 0
            # Apply selected styling
            self._update_selection_styling(0)
            # Also update our selected_job and post the selection message
            self.selected_job = sorted_jobs[0]
            self.post_message(self.JobSelected(sorted_jobs[0]))

    def _get_status_priority(self, status: int) -> int:
        """Get priority for sorting jobs by status."""
        # Running jobs first, then idle, then others
        priority_map = {
            2: 0,  # Running
            1: 1,  # Idle
            6: 2,  # Transferring Output
            5: 3,  # Held
            7: 4,  # Suspended
            4: 5,  # Completed
            3: 6,  # Removed
            0: 7,  # Unexpanded
        }
        return priority_map.get(status, 8)

    def _update_selection_styling(self, selected_index: int) -> None:
        """Update the selection styling for job items."""
        job_list = self.query_one("#job-list", ListView)
        for i, item in enumerate(job_list.children):
            if isinstance(item, CondorJobItem):
                if i == selected_index:
                    item.add_class("job-item-selected")
                else:
                    item.remove_class("job-item-selected")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle job selection."""
        if isinstance(event.item, CondorJobItem):
            # Get the index of the selected item
            job_list = self.query_one("#job-list", ListView)
            selected_index = list(job_list.children).index(event.item)

            # Update selection styling
            self._update_selection_styling(selected_index)

            self.selected_job = event.item.job
            self.post_message(self.JobSelected(event.item.job))

    def add_job(self, job: CondorJob) -> None:
        """Add a new job to the list."""
        new_jobs = list(self.jobs)
        new_jobs.append(job)
        self.jobs = new_jobs

    def update_job(self, updated_job: CondorJob) -> None:
        """Update an existing job in the list."""
        new_jobs = []
        for job in self.jobs:
            if job.job_id == updated_job.job_id:
                new_jobs.append(updated_job)
            else:
                new_jobs.append(job)
        self.jobs = new_jobs

    def remove_job(self, job_id: str) -> None:
        """Remove a job from the list."""
        new_jobs = [job for job in self.jobs if job.job_id != job_id]
        self.jobs = new_jobs

    def filter_jobs(
        self, status: Optional[str] = None, user: Optional[str] = None
    ) -> None:
        """Filter jobs by status or user (placeholder for future implementation)."""
        # This could be implemented to filter the displayed jobs
        pass

    class JobSelected(Message):
        """Message sent when a job is selected."""

        def __init__(self, job: CondorJob) -> None:
            super().__init__()
            self.job = job
