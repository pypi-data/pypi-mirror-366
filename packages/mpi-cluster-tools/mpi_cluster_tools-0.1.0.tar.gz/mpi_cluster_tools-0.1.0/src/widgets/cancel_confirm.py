from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Label


class ConfirmCancelScreen(ModalScreen):
    """A modal screen to confirm job cancellation."""

    BINDINGS = [
        ("escape", "dismiss", "Dismiss"),
        ("enter", "dismiss", "Dismiss"),
        ("y", "confirm", "Confirm"),
        ("n", "cancel", "Cancel"),
    ]

    def __init__(self, job_id: str, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id

    def compose(self):
        """Compose the confirmation dialog."""
        cont = Container(
            Label(f"Are you sure you want to cancel job {self.job_id}?", id="question"),
            Label("Press 'y' to remove job, 'n' to keep"),
            id="dialog",
        )
        cont.border_title = f"Cancel Job {self.job_id}"
        yield cont

    def _action_confirm(self) -> None:
        """Action to confirm the job cancellation."""
        self.dismiss(True)

    def _action_cancel(self) -> None:
        """Action to cancel the job cancellation."""
        self.dismiss(False)

    def _action_dismiss(self) -> None:
        """Action to dismiss the confirmation dialog."""
        self.dismiss(False)
