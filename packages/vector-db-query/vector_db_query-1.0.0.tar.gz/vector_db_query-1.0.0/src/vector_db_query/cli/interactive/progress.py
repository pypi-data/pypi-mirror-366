"""Advanced progress management for long-running operations."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from threading import Thread, Event
import queue

from rich.console import Console
from rich.progress import (
    Progress, ProgressColumn, Task, TextColumn, BarColumn,
    TimeRemainingColumn, SpinnerColumn, TimeElapsedColumn,
    DownloadColumn, TransferSpeedColumn, FileSizeColumn
)
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from .base import BaseUIComponent, UIConfig
from .styles import get_icon, get_color


class TaskStatus(Enum):
    """Task status enumeration."""
    
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressTask:
    """Progress task definition."""
    
    id: str
    name: str
    total: Optional[int] = None
    current: int = 0
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        if self.total is None or self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time."""
        if self.start_time is None:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Get estimated remaining time."""
        if self.total is None or self.current == 0 or self.elapsed_time is None:
            return None
        
        rate = self.current / self.elapsed_time.total_seconds()
        remaining = self.total - self.current
        if rate > 0:
            return timedelta(seconds=remaining / rate)
        return None
    
    @property
    def throughput(self) -> Optional[float]:
        """Get throughput (items per second)."""
        elapsed = self.elapsed_time
        if elapsed is None or elapsed.total_seconds() == 0:
            return None
        return self.current / elapsed.total_seconds()


class ProgressManager(BaseUIComponent):
    """Manage multiple progress tasks."""
    
    def __init__(
        self,
        auto_refresh: bool = True,
        refresh_rate: float = 0.1,
        show_overall: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize progress manager.
        
        Args:
            auto_refresh: Auto-refresh display
            refresh_rate: Refresh rate in seconds
            show_overall: Show overall progress
            config: UI configuration
        """
        super().__init__(config)
        self.auto_refresh = auto_refresh
        self.refresh_rate = refresh_rate
        self.show_overall = show_overall
        self.tasks: Dict[str, ProgressTask] = {}
        self._progress: Optional[Progress] = None
        self._live: Optional[Live] = None
        self._stop_event = Event()
        self._update_queue: queue.Queue = queue.Queue()
        self._task_map: Dict[str, int] = {}  # Map task ID to progress task ID
    
    def create_task(
        self,
        task_id: str,
        name: str,
        total: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProgressTask:
        """Create a new progress task.
        
        Args:
            task_id: Unique task ID
            name: Task name
            total: Total units (None for indeterminate)
            metadata: Task metadata
            
        Returns:
            Progress task
        """
        task = ProgressTask(
            id=task_id,
            name=name,
            total=total,
            metadata=metadata or {}
        )
        self.tasks[task_id] = task
        
        # Queue update
        self._update_queue.put(("create", task))
        
        return task
    
    def update_task(
        self,
        task_id: str,
        advance: Optional[int] = None,
        current: Optional[int] = None,
        total: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update task progress.
        
        Args:
            task_id: Task ID
            advance: Units to advance
            current: Set current value
            total: Update total
            status: Update status
            error: Error message
            metadata: Update metadata
        """
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        
        # Update values
        if advance is not None:
            task.current += advance
        if current is not None:
            task.current = current
        if total is not None:
            task.total = total
        if status is not None:
            task.status = status
            if status == TaskStatus.RUNNING and task.start_time is None:
                task.start_time = datetime.now()
            elif task.is_complete and task.end_time is None:
                task.end_time = datetime.now()
        if error is not None:
            task.error = error
        if metadata is not None:
            task.metadata.update(metadata)
        
        # Queue update
        self._update_queue.put(("update", task))
    
    def complete_task(self, task_id: str, success: bool = True) -> None:
        """Mark task as complete.
        
        Args:
            task_id: Task ID
            success: Whether task succeeded
        """
        status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        self.update_task(task_id, status=status)
    
    def cancel_task(self, task_id: str) -> None:
        """Cancel task.
        
        Args:
            task_id: Task ID
        """
        self.update_task(task_id, status=TaskStatus.CANCELLED)
    
    def pause_task(self, task_id: str) -> None:
        """Pause task.
        
        Args:
            task_id: Task ID
        """
        self.update_task(task_id, status=TaskStatus.PAUSED)
    
    def resume_task(self, task_id: str) -> None:
        """Resume task.
        
        Args:
            task_id: Task ID
        """
        self.update_task(task_id, status=TaskStatus.RUNNING)
    
    def start(self) -> None:
        """Start progress display."""
        if self._progress is not None:
            return
        
        # Create progress display
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            refresh_per_second=1 / self.refresh_rate if self.auto_refresh else 1
        )
        
        # Start live display
        self._live = Live(self._progress, console=self.console, refresh_per_second=1 / self.refresh_rate)
        self._live.start()
        
        # Start update thread
        if self.auto_refresh:
            self._stop_event.clear()
            self._update_thread = Thread(target=self._process_updates, daemon=True)
            self._update_thread.start()
    
    def stop(self) -> None:
        """Stop progress display."""
        self._stop_event.set()
        
        if self._live:
            self._live.stop()
            self._live = None
        
        if self._progress:
            self._progress = None
        
        self._task_map.clear()
    
    def _process_updates(self) -> None:
        """Process update queue."""
        while not self._stop_event.is_set():
            try:
                # Get update with timeout
                update = self._update_queue.get(timeout=0.1)
                action, task = update
                
                if action == "create":
                    self._create_progress_task(task)
                elif action == "update":
                    self._update_progress_task(task)
                
            except queue.Empty:
                continue
            except Exception:
                # Ignore errors in update thread
                pass
    
    def _create_progress_task(self, task: ProgressTask) -> None:
        """Create progress bar task.
        
        Args:
            task: Progress task
        """
        if self._progress is None or task.id in self._task_map:
            return
        
        # Create progress task
        progress_task_id = self._progress.add_task(
            task.name,
            total=task.total,
            completed=task.current
        )
        
        self._task_map[task.id] = progress_task_id
    
    def _update_progress_task(self, task: ProgressTask) -> None:
        """Update progress bar task.
        
        Args:
            task: Progress task
        """
        if self._progress is None or task.id not in self._task_map:
            return
        
        progress_task_id = self._task_map[task.id]
        
        # Update progress
        self._progress.update(
            progress_task_id,
            completed=task.current,
            total=task.total,
            description=self._format_task_description(task)
        )
        
        # Remove if complete
        if task.is_complete:
            self._progress.remove_task(progress_task_id)
            del self._task_map[task.id]
    
    def _format_task_description(self, task: ProgressTask) -> str:
        """Format task description.
        
        Args:
            task: Progress task
            
        Returns:
            Formatted description
        """
        desc = task.name
        
        # Add status indicator
        if task.status == TaskStatus.COMPLETED:
            desc = f"[green]✓[/green] {desc}"
        elif task.status == TaskStatus.FAILED:
            desc = f"[red]✗[/red] {desc}"
        elif task.status == TaskStatus.CANCELLED:
            desc = f"[yellow]⚠[/yellow] {desc}"
        elif task.status == TaskStatus.PAUSED:
            desc = f"[dim]⏸[/dim] {desc}"
        
        return desc
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary.
        
        Returns:
            Summary statistics
        """
        total_tasks = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        
        # Calculate overall progress
        overall_progress = 0.0
        if total_tasks > 0:
            task_progresses = []
            for task in self.tasks.values():
                if task.status == TaskStatus.COMPLETED:
                    task_progresses.append(100.0)
                elif task.status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task_progresses.append(task.progress_percent)
                elif task.total is not None:
                    task_progresses.append(task.progress_percent)
                else:
                    task_progresses.append(0.0)
            
            overall_progress = sum(task_progresses) / len(task_progresses)
        
        return {
            "total": total_tasks,
            "completed": completed,
            "failed": failed,
            "running": running,
            "overall_progress": overall_progress
        }
    
    def render(self) -> None:
        """Render progress display."""
        self.start()


class MultiProgressDisplay(BaseUIComponent):
    """Display multiple progress bars with statistics."""
    
    def __init__(
        self,
        title: str = "Progress",
        show_stats: bool = True,
        show_timeline: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize multi-progress display.
        
        Args:
            title: Display title
            show_stats: Show statistics panel
            show_timeline: Show timeline
            config: UI configuration
        """
        super().__init__(config)
        self.title = title
        self.show_stats = show_stats
        self.show_timeline = show_timeline
        self.manager = ProgressManager(config=config)
        self._layout: Optional[Layout] = None
        self._live: Optional[Live] = None
    
    def start(self) -> None:
        """Start display."""
        # Create layout
        self._layout = self._create_layout()
        
        # Start live display
        self._live = Live(
            self._layout,
            console=self.console,
            refresh_per_second=4
        )
        self._live.start()
        
        # Start manager
        self.manager.start()
        
        # Start update loop
        self._stop_event = Event()
        self._update_thread = Thread(target=self._update_display, daemon=True)
        self._update_thread.start()
    
    def stop(self) -> None:
        """Stop display."""
        self._stop_event.set()
        
        if self._live:
            self._live.stop()
            self._live = None
        
        self.manager.stop()
    
    def _create_layout(self) -> Layout:
        """Create display layout.
        
        Returns:
            Layout object
        """
        layout = Layout()
        
        # Create sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main section
        if self.show_stats and self.show_timeline:
            layout["main"].split_row(
                Layout(name="progress", ratio=2),
                Layout(name="stats", ratio=1),
                Layout(name="timeline", ratio=1)
            )
        elif self.show_stats:
            layout["main"].split_row(
                Layout(name="progress", ratio=2),
                Layout(name="stats", ratio=1)
            )
        else:
            layout["main"].update(name="progress")
        
        return layout
    
    def _update_display(self) -> None:
        """Update display loop."""
        while not self._stop_event.is_set():
            try:
                # Update header
                self._layout["header"].update(self._render_header())
                
                # Update progress
                if "progress" in self._layout:
                    self._layout["progress"].update(self._render_progress())
                
                # Update stats
                if self.show_stats and "stats" in self._layout:
                    self._layout["stats"].update(self._render_stats())
                
                # Update timeline
                if self.show_timeline and "timeline" in self._layout:
                    self._layout["timeline"].update(self._render_timeline())
                
                # Update footer
                self._layout["footer"].update(self._render_footer())
                
                # Sleep
                time.sleep(0.25)
                
            except Exception:
                # Ignore errors in update loop
                pass
    
    def _render_header(self) -> Panel:
        """Render header.
        
        Returns:
            Header panel
        """
        summary = self.manager.get_summary()
        
        header_text = Text(self.title, style="bold")
        if summary["total"] > 0:
            header_text.append(f" - {summary['overall_progress']:.1f}% Complete", style="cyan")
        
        return Panel(header_text, border_style="blue")
    
    def _render_progress(self) -> Panel:
        """Render progress bars.
        
        Returns:
            Progress panel
        """
        # The actual progress bars are rendered by the manager
        # This is a placeholder for the layout
        return Panel(
            "Progress bars will appear here",
            title="Tasks",
            border_style="green"
        )
    
    def _render_stats(self) -> Panel:
        """Render statistics.
        
        Returns:
            Stats panel
        """
        summary = self.manager.get_summary()
        
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", justify="right")
        
        stats_table.add_row("Total Tasks", str(summary["total"]))
        stats_table.add_row("Completed", f"[green]{summary['completed']}[/green]")
        stats_table.add_row("Failed", f"[red]{summary['failed']}[/red]")
        stats_table.add_row("Running", f"[yellow]{summary['running']}[/yellow]")
        stats_table.add_row("", "")
        stats_table.add_row("Progress", f"{summary['overall_progress']:.1f}%")
        
        # Add throughput
        total_throughput = 0.0
        for task in self.manager.tasks.values():
            if task.throughput:
                total_throughput += task.throughput
        
        if total_throughput > 0:
            stats_table.add_row("Throughput", f"{total_throughput:.1f}/s")
        
        return Panel(stats_table, title="Statistics", border_style="yellow")
    
    def _render_timeline(self) -> Panel:
        """Render timeline.
        
        Returns:
            Timeline panel
        """
        timeline_items = []
        
        # Get recent task events
        events = []
        for task in self.manager.tasks.values():
            if task.start_time:
                events.append((task.start_time, f"Started: {task.name}", "cyan"))
            if task.end_time:
                if task.status == TaskStatus.COMPLETED:
                    events.append((task.end_time, f"Completed: {task.name}", "green"))
                elif task.status == TaskStatus.FAILED:
                    events.append((task.end_time, f"Failed: {task.name}", "red"))
        
        # Sort by time
        events.sort(key=lambda x: x[0], reverse=True)
        
        # Format timeline
        for timestamp, event, color in events[:10]:
            time_str = timestamp.strftime("%H:%M:%S")
            timeline_items.append(f"[{color}]{time_str}[/{color}] {event}")
        
        if timeline_items:
            content = "\n".join(timeline_items)
        else:
            content = "[dim]No events yet[/dim]"
        
        return Panel(content, title="Timeline", border_style="blue")
    
    def _render_footer(self) -> Panel:
        """Render footer.
        
        Returns:
            Footer panel
        """
        help_text = "[dim]Press Ctrl+C to cancel[/dim]"
        return Panel(help_text, border_style="dim")
    
    def render(self) -> None:
        """Render display."""
        self.start()


class ProgressGroup:
    """Group related progress tasks."""
    
    def __init__(self, name: str, manager: ProgressManager):
        """Initialize progress group.
        
        Args:
            name: Group name
            manager: Progress manager
        """
        self.name = name
        self.manager = manager
        self.task_ids: List[str] = []
    
    def add_task(
        self,
        name: str,
        total: Optional[int] = None,
        weight: float = 1.0
    ) -> str:
        """Add task to group.
        
        Args:
            name: Task name
            total: Total units
            weight: Task weight for overall progress
            
        Returns:
            Task ID
        """
        task_id = f"{self.name}_{len(self.task_ids)}"
        task = self.manager.create_task(task_id, name, total)
        task.metadata["weight"] = weight
        task.metadata["group"] = self.name
        self.task_ids.append(task_id)
        return task_id
    
    def update(self, task_id: str, **kwargs) -> None:
        """Update task in group.
        
        Args:
            task_id: Task ID
            **kwargs: Update arguments
        """
        if task_id in self.task_ids:
            self.manager.update_task(task_id, **kwargs)
    
    def get_progress(self) -> float:
        """Get group progress.
        
        Returns:
            Progress percentage
        """
        if not self.task_ids:
            return 0.0
        
        total_weight = 0.0
        weighted_progress = 0.0
        
        for task_id in self.task_ids:
            if task_id in self.manager.tasks:
                task = self.manager.tasks[task_id]
                weight = task.metadata.get("weight", 1.0)
                total_weight += weight
                weighted_progress += task.progress_percent * weight
        
        if total_weight > 0:
            return weighted_progress / total_weight
        return 0.0


def create_file_progress(
    files: List[str],
    operation: str = "Processing"
) -> Callable[[str, int], None]:
    """Create file processing progress tracker.
    
    Args:
        files: List of files
        operation: Operation name
        
    Returns:
        Update function
    """
    manager = ProgressManager()
    manager.start()
    
    # Create task for each file
    task_ids = {}
    for file in files:
        task_id = f"file_{len(task_ids)}"
        manager.create_task(task_id, f"{operation}: {file}", total=100)
        task_ids[file] = task_id
    
    def update(file: str, progress: int) -> None:
        """Update file progress."""
        if file in task_ids:
            manager.update_task(task_ids[file], current=progress)
            if progress >= 100:
                manager.complete_task(task_ids[file])
    
    return update