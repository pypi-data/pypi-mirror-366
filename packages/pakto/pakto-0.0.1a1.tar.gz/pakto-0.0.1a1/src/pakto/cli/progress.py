"""Progress display for CLI operations."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Optional, Union

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)


class ProgressEventType(Enum):
    """Enumeration of progress event types for structured event handling."""

    DOWNLOAD_START = "download_start"
    DOWNLOAD_PROGRESS = "download_progress"
    DOWNLOAD_COMPLETE = "download_complete"
    PACK_START = "pack_start"
    BUNDLE_EXISTS = "bundle_exists"
    ARTIFACT_START = "artifact_start"
    ARTIFACT_PROGRESS = "artifact_progress"
    ARTIFACT_COMPLETE = "artifact_complete"
    LAYER_CREATION_START = "layer_creation_start"
    LAYER_CREATION_PROGRESS = "layer_creation_progress"
    LAYER_CREATION_COMPLETE = "layer_creation_complete"
    BUNDLE_ASSEMBLY = "bundle_assembly"
    PUSH_START = "push_start"
    PUSH_COMPLETE = "push_complete"
    PUSH_ERROR = "push_error"
    ENTRYPOINT_CACHING = "entrypoint_caching"
    ENTRYPOINT_CACHED = "entrypoint_cached"
    ENTRYPOINT_VERIFICATION = "entrypoint_verification"
    ENTRYPOINT_RETRIEVED = "entrypoint_retrieved"
    ENTRYPOINT_ERROR = "entrypoint_error"
    LOCK_START = "lock_start"
    LOCK_COMPLETE = "lock_complete"
    BUNDLE_START = "bundle_start"
    BUNDLE_COMPLETE = "bundle_complete"
    # Apply command events
    APPLY_START = "apply_start"
    APPLY_COMPLETE = "apply_complete"
    APPLY_ERROR = "apply_error"
    BUNDLE_CREATION = "bundle_creation"
    BUNDLE_CREATED = "bundle_created"
    DEPLOYING = "deploying"
    ARTIFACTS_COMPLETE = "artifacts_complete"
    EXECUTING_ENTRYPOINT = "executing_entrypoint"
    ENTRYPOINT_COMPLETE = "entrypoint_complete"


@dataclass
class ProgressEvent:
    """Structured progress event for type-safe progress reporting."""

    event_type: ProgressEventType
    name: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None
    bytes_downloaded: Optional[int] = None
    total_bytes: Optional[int] = None
    registry: Optional[str] = None
    digest: Optional[str] = None
    error: Optional[str] = None
    checksum: Optional[str] = None
    total_artifacts: Optional[int] = None
    # Apply-specific fields
    bundle: Optional[str] = None
    lockfile: Optional[str] = None
    output_path: Optional[str] = None
    current: Optional[int] = None
    total: Optional[int] = None
    artifact: Optional[str] = None
    script: Optional[str] = None
    returncode: Optional[int] = None


def format_bytes(num_bytes: int) -> str:
    """Convert bytes to human readable format."""
    size_float = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_float) < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} PB"


class ProgressDisplay:
    """Manages progress display for concurrent downloads."""

    def __init__(self):
        self.progress: Optional[Progress] = None
        self.tasks: Dict[str, TaskID] = {}

    def start(self):
        """Start the progress display."""
        if self.progress is None:
            self.progress = Progress(
                TextColumn("[bold blue]{task.fields[name]}", justify="right"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TimeRemainingColumn(),
            )
            self.progress.start()

    def stop(self):
        """Stop the progress display."""
        if self.progress is not None:
            self.progress.stop()
            self.progress = None
            self.tasks.clear()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


def create_progress_callback(display: ProgressDisplay) -> Callable:
    """Create a progress callback function for the given display."""

    def callback(event: Union[ProgressEvent, Dict]):
        """Process progress events."""
        # Handle both structured ProgressEvent and legacy dict format
        if isinstance(event, ProgressEvent):
            event_type = event.event_type.value
            name = event.name or "unknown"
            bytes_downloaded = event.bytes_downloaded
            total_bytes = event.total_bytes
        else:
            # Legacy dict format
            event_type = event.get("type", "")
            name = event.get("name", "unknown")
            event.get("message")
            event.get("status")
            bytes_downloaded = event.get("bytes_downloaded", 0)
            total_bytes = event.get("total_bytes")

        if (
            event_type == "download_start"
            and display.progress
            and name not in display.tasks
        ):
            task_id = display.progress.add_task(
                f"Downloading {name}",
                name=name,
                total=None,  # Will be updated when we know the size
            )
            display.tasks[name] = task_id

        elif (
            event_type == "download_progress"
            and display.progress
            and name in display.tasks
        ):
            task_id = display.tasks[name]

            if total_bytes:
                display.progress.update(
                    task_id, completed=bytes_downloaded, total=total_bytes
                )
            else:
                # Unknown total size
                display.progress.update(task_id, completed=bytes_downloaded)

        elif (
            event_type == "download_complete"
            and display.progress
            and name in display.tasks
        ):
            task_id = display.tasks[name]
            # Set to 100% complete
            total = display.progress.tasks[task_id].total
            if total:
                display.progress.update(task_id, completed=total)
            # Remove from active tasks
            del display.tasks[name]

        # Handle layer creation progress with progress bars
        elif event_type == "layer_creation_start" and display.progress:
            name = event.get("name") if isinstance(event, dict) else event.name
            if name and name not in display.tasks:
                task_id = display.progress.add_task(
                    f"Creating layer for {name}",
                    name=name,
                    total=100,  # Layer creation is typically quick, use percentage
                )
                display.tasks[name] = task_id

        elif event_type == "layer_creation_progress" and display.progress:
            name = event.get("name") if isinstance(event, dict) else event.name
            current = event.get("current") if isinstance(event, dict) else event.current
            if name in display.tasks and current is not None:
                task_id = display.tasks[name]
                display.progress.update(task_id, completed=current)

        elif event_type == "layer_creation_complete" and display.progress:
            name = event.get("name") if isinstance(event, dict) else event.name
            if name in display.tasks:
                task_id = display.tasks[name]
                display.progress.update(task_id, completed=100)
                del display.tasks[name]

        # Handle pack-specific events
        elif (
            event_type == "pack_start"
            or event_type == "bundle_exists"
            or event_type == "bundle_assembly"
            or event_type == "push_start"
            or event_type == "push_complete"
            or event_type == "entrypoint_verification"
            or event_type == "entrypoint_retrieved"
            or event_type == "artifact_start"
            or event_type == "artifact_progress"
            or event_type == "artifact_complete"
        ):
            if display.progress:
                message = (
                    event.get("message") if isinstance(event, dict) else event.message
                )
                if message:
                    display.progress.print(message)

        elif event_type == "push_error" or event_type == "entrypoint_error":
            if display.progress:
                message = (
                    event.get("message") if isinstance(event, dict) else event.message
                )
                if message:
                    display.progress.print(f"[red]{message}[/red]")

    return callback


def create_apply_progress_callback(display: ProgressDisplay) -> Callable:
    """Create a progress callback function specifically for apply operations."""

    def callback(event: Union[ProgressEvent, Dict]):
        """Process apply-specific progress events."""
        # Handle both structured ProgressEvent and legacy dict format
        if isinstance(event, ProgressEvent):
            event_type = event.event_type.value
            message = event.message
            bundle = event.bundle
            lockfile = event.lockfile
            current = event.current
            total = event.total
            artifact = event.artifact
            script = event.script
            error = event.error
        else:
            # Legacy dict format
            event_type = event.get("type", "")
            message = event.get("message", "")
            bundle = event.get("bundle")
            lockfile = event.get("lockfile")
            current = event.get("current")
            total = event.get("total")
            artifact = event.get("artifact")
            script = event.get("script")
            error = event.get("error")

        # Handle apply-specific events
        if event_type == "apply_start":
            if bundle:
                display.progress.print(f"[cyan]Applying bundle:[/cyan] {bundle}")
            elif lockfile:
                display.progress.print(f"[cyan]Applying lockfile:[/cyan] {lockfile}")
            if message:
                display.progress.print(f"[dim]{message}[/dim]")

        elif event_type == "apply_complete":
            if message:
                display.progress.print(f"[green]✓[/green] {message}")

        elif event_type == "apply_error":
            if error:
                display.progress.print(f"[red]✗[/red] {error}")
            if message:
                display.progress.print(f"[red]{message}[/red]")

        elif event_type == "bundle_creation":
            if message:
                display.progress.print("[yellow]Creating temporary bundle...[/yellow]")

        elif event_type == "bundle_created":
            if message:
                display.progress.print(f"[green]✓[/green] {message}")

        elif event_type == "deploying":
            if artifact and total:
                progress_text = f"[cyan]Deploying {artifact}[/cyan] ({current}/{total})"
                display.progress.print(progress_text)

        elif event_type == "artifacts_complete":
            if total:
                display.progress.print(f"[green]✓[/green] Deployed {total} artifacts")

        elif event_type == "executing_entrypoint":
            if script:
                display.progress.print(
                    f"[yellow]Executing entrypoint:[/yellow] {script}"
                )

        elif event_type == "entrypoint_complete":
            if script:
                display.progress.print(
                    f"[green]✓[/green] Entrypoint {script} completed"
                )

        # Also handle legacy download events for compatibility
        elif event_type in ["download_start", "download_progress", "download_complete"]:
            # Delegate to the main progress callback
            create_progress_callback(display)(event)

    return callback
