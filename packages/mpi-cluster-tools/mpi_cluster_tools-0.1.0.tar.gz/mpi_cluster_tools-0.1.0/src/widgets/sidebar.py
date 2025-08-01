from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

from ..htcondor.htcondor import HTCondorClient
from ..htcondor.types import CondorJob
from .condor_job_list import CondorJobList


class JobsSidebar(Vertical):
    """Sidebar for job management, displays HTCondor jobs"""

    jobs: reactive[List[CondorJob]] = reactive([])
    current_job: reactive[Optional[CondorJob]] = reactive(None)

    def __init__(
        self,
        htcondor_client: Optional[HTCondorClient] = None,
        username: Optional[str] = None,
        id: str = "sidebar",
        classes: str = "",
    ):
        classes = f"{classes} focus-container".strip()
        super().__init__(id=id, classes=classes)
        self.htcondor_client = htcondor_client
        self.username = username
        self.border_title = f"Cluster Jobs for {username}"

    def compose(self) -> ComposeResult:
        """Compose the sidebar layout."""
        yield CondorJobList(jobs=self.jobs, id="condor-job-list")

    def on_mount(self) -> None:
        """Load jobs when the sidebar is mounted."""
        if self.htcondor_client and self.username:
            self.refresh_jobs()

    def refresh_jobs(self) -> None:
        """Refresh the job list from HTCondor."""
        if not self.htcondor_client or not self.username:
            print("HTCondor client or username not set, cannot refresh jobs")
            return

        try:
            jobs = self.htcondor_client.get_user_jobs(self.username)
            self.jobs = jobs
            print(f"Loaded {len(jobs)} jobs for user {self.username}")
            print(jobs)

            # Update the job list widget with new jobs
            job_list = self.query_one("#condor-job-list", CondorJobList)
            job_list.jobs = jobs
        except Exception as e:
            print(f"Failed to load jobs: {e}")
            self.jobs = []

            # Clear the job list widget on error
            job_list = self.query_one("#condor-job-list", CondorJobList)
            job_list.jobs = []

    def on_condor_job_list_job_selected(self, event: CondorJobList.JobSelected) -> None:
        """Handle job selection from the job list."""
        self.current_job = event.job
        self.post_message(self.JobSelected(event.job))

    def set_htcondor_client(self, client: HTCondorClient, username: str) -> None:
        """Set the HTCondor client and username, then refresh jobs."""
        self.htcondor_client = client
        self.username = username
        self.border_title = f"Cluster Jobs for {username}"
        self.refresh_jobs()

    class JobSelected(Message):
        """Message sent when a job is selected"""

        def __init__(self, job: CondorJob):
            super().__init__()
            self.job = job
