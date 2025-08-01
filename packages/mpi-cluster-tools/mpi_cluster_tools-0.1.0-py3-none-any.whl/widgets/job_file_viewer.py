from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive

from ..htcondor.types import CondorJob
from ..ssh.cluster import SSHClient
from .file_tail_viewer import FileTailViewer


class JobFileViewer(Vertical):
    """A widget that displays the log, error, and output files of a HTCondor job."""

    current_job: reactive[Optional[CondorJob]] = reactive(None)

    def __init__(self, ssh_client: Optional[SSHClient] = None, **kwargs):
        # Add focus-container class
        if "classes" in kwargs:
            kwargs["classes"] = f"{kwargs['classes']} focus-container".strip()
        else:
            kwargs["classes"] = "focus-container"
        super().__init__(**kwargs)
        self.ssh_client = ssh_client

    def compose(self) -> ComposeResult:
        """Compose the job file viewer layout with three stacked file viewers."""
        yield FileTailViewer(
            "Job Log File",
            ssh_client=self.ssh_client,
            id="log-viewer",
            classes="file-viewer",
        )
        yield FileTailViewer(
            "Error Output",
            ssh_client=self.ssh_client,
            id="error-viewer",
            classes="file-viewer",
        )
        yield FileTailViewer(
            "Standard Output",
            ssh_client=self.ssh_client,
            id="output-viewer",
            classes="file-viewer",
        )

    def on_mount(self) -> None:
        """Initialize after the widget is mounted."""
        # Update SSH client for child viewers if we have one
        if self.ssh_client:
            self._update_child_ssh_clients()

        # Set up initial state - clear viewers if no job is set
        if self.current_job is None:
            self.clear_file_viewers()

    def _update_child_ssh_clients(self) -> None:
        """Update SSH client for all child file viewers."""
        if not self.is_mounted:
            return

        try:
            log_viewer = self.query_one("#log-viewer", FileTailViewer)
            error_viewer = self.query_one("#error-viewer", FileTailViewer)
            output_viewer = self.query_one("#output-viewer", FileTailViewer)

            log_viewer.ssh_client = self.ssh_client
            error_viewer.ssh_client = self.ssh_client
            output_viewer.ssh_client = self.ssh_client
        except Exception:
            # Widget not fully composed yet, ignore
            pass

    def watch_current_job(self, new_job: Optional[CondorJob]) -> None:
        """Called when current_job changes - update all file viewers."""
        # Only update if the widget is mounted
        if not self.is_mounted:
            return

        if new_job:
            self.update_file_viewers(new_job)
        else:
            self.clear_file_viewers()

    def update_file_viewers(self, job: CondorJob) -> None:
        """Update all file viewers with the job's file paths."""
        # Only update if the widget is mounted and composed
        if not self.is_mounted:
            return

        try:
            log_viewer = self.query_one("#log-viewer", FileTailViewer)
            error_viewer = self.query_one("#error-viewer", FileTailViewer)
            output_viewer = self.query_one("#output-viewer", FileTailViewer)

            # Resolve file paths (prepend iwd for relative paths)
            log_path = self._resolve_file_path(job.user_log, job.iwd)
            error_path = self._resolve_file_path(job.error_file, job.iwd)
            output_path = self._resolve_file_path(job.output_file, job.iwd)

            # Set file paths for each viewer (with debug info)
            print(
                f"Setting job files - Log: {log_path}, Error: {error_path}, Output: {output_path}"
            )
            log_viewer.set_file(log_path)
            error_viewer.set_file(error_path)
            output_viewer.set_file(output_path)
        except Exception as e:
            print(f"Error updating file viewers: {e}")
            # Widget not fully composed yet, ignore
            pass

    def clear_file_viewers(self) -> None:
        """Clear all file viewers."""
        # Only update if the widget is mounted and composed
        if not self.is_mounted:
            return

        try:
            log_viewer = self.query_one("#log-viewer", FileTailViewer)
            error_viewer = self.query_one("#error-viewer", FileTailViewer)
            output_viewer = self.query_one("#output-viewer", FileTailViewer)

            log_viewer.set_file(None)
            error_viewer.set_file(None)
            output_viewer.set_file(None)
        except Exception:
            # Widget not fully composed yet, ignore
            pass

    def set_job(self, job: Optional[CondorJob]) -> None:
        """Set the current job to display."""
        self.current_job = job

    def set_ssh_client(self, ssh_client: Optional[SSHClient]) -> None:
        """Set the SSH client for this viewer and all child file viewers."""
        self.ssh_client = ssh_client
        self._update_child_ssh_clients()

    def refresh_all(self) -> None:
        """Refresh content of all file viewers."""
        # Only update if the widget is mounted and composed
        if not self.is_mounted:
            return

        try:
            log_viewer = self.query_one("#log-viewer", FileTailViewer)
            error_viewer = self.query_one("#error-viewer", FileTailViewer)
            output_viewer = self.query_one("#output-viewer", FileTailViewer)

            log_viewer.refresh_content()
            error_viewer.refresh_content()
            output_viewer.refresh_content()
        except Exception:
            # Widget not fully composed yet, ignore
            pass

    def _resolve_file_path(
        self, file_path: Optional[str], iwd: Optional[str]
    ) -> Optional[str]:
        """Resolve file path by prepending iwd for relative paths."""
        if not file_path:
            return file_path

        # If path is already absolute, return as is
        if file_path.startswith("/"):
            return file_path

        # If we have an iwd and the path is relative, prepend iwd
        if iwd:
            # Ensure iwd ends with / for proper path joining
            iwd_normalized = iwd.rstrip("/") + "/"
            return iwd_normalized + file_path

        # No iwd available, return original path
        return file_path
