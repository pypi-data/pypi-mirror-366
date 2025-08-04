"""Demo script for progress management components."""

import time
import random
import asyncio
from pathlib import Path
from rich.console import Console

from .progress import (
    ProgressManager, MultiProgressDisplay, ProgressGroup,
    TaskStatus, create_file_progress
)


def demo_basic_progress():
    """Demo basic progress tracking."""
    console = Console()
    
    console.print("\n[bold]Basic Progress Tracking Demo[/bold]\n")
    
    # Create progress manager
    manager = ProgressManager()
    manager.start()
    
    try:
        # Create tasks
        task1 = manager.create_task("download", "Downloading files", total=100)
        task2 = manager.create_task("process", "Processing data", total=50)
        task3 = manager.create_task("upload", "Uploading results", total=None)  # Indeterminate
        
        # Simulate work
        for i in range(100):
            # Update task 1
            manager.update_task("download", advance=1)
            
            # Update task 2 every other iteration
            if i % 2 == 0 and i < 100:
                manager.update_task("process", advance=1)
            
            # Update task 3 (spinner)
            manager.update_task("upload", status=TaskStatus.RUNNING)
            
            time.sleep(0.05)
        
        # Complete tasks
        manager.complete_task("download")
        manager.complete_task("process")
        manager.complete_task("upload")
        
        time.sleep(1)
        
    finally:
        manager.stop()
    
    console.print("\n[green]All tasks completed![/green]")


def demo_multi_progress():
    """Demo multi-progress display with stats."""
    console = Console()
    
    console.print("\n[bold]Multi-Progress Display Demo[/bold]\n")
    console.print("Simulating multiple concurrent operations...\n")
    
    # Create display
    display = MultiProgressDisplay(
        title="Batch Processing",
        show_stats=True,
        show_timeline=True
    )
    
    display.start()
    
    try:
        # Create multiple tasks
        tasks = [
            ("file1.txt", 80),
            ("file2.pdf", 120),
            ("file3.doc", 60),
            ("file4.csv", 100),
            ("file5.json", 40),
        ]
        
        # Create tasks
        for i, (filename, size) in enumerate(tasks):
            display.manager.create_task(
                f"task_{i}",
                f"Processing {filename}",
                total=size
            )
        
        # Simulate processing with varying speeds
        completed = set()
        
        while len(completed) < len(tasks):
            for i, (filename, size) in enumerate(tasks):
                task_id = f"task_{i}"
                
                if task_id in completed:
                    continue
                
                # Random progress
                advance = random.randint(1, 5)
                display.manager.update_task(task_id, advance=advance)
                
                # Check if complete
                task = display.manager.tasks[task_id]
                if task.current >= task.total:
                    # Random success/failure
                    if random.random() > 0.1:  # 90% success rate
                        display.manager.complete_task(task_id)
                    else:
                        display.manager.update_task(
                            task_id,
                            status=TaskStatus.FAILED,
                            error="Simulated error"
                        )
                    completed.add(task_id)
            
            time.sleep(0.1)
        
        # Let display show final state
        time.sleep(2)
        
    finally:
        display.stop()
    
    console.print("\n[cyan]Processing complete![/cyan]")


def demo_progress_groups():
    """Demo progress groups for related tasks."""
    console = Console()
    
    console.print("\n[bold]Progress Groups Demo[/bold]\n")
    console.print("Tracking grouped operations...\n")
    
    manager = ProgressManager()
    manager.start()
    
    try:
        # Create groups
        download_group = ProgressGroup("Downloads", manager)
        process_group = ProgressGroup("Processing", manager)
        
        # Add tasks to download group
        files_to_download = ["data1.zip", "data2.zip", "data3.zip"]
        download_tasks = []
        for file in files_to_download:
            task_id = download_group.add_task(f"Download {file}", total=100)
            download_tasks.append(task_id)
        
        # Add tasks to process group
        process_tasks = []
        for i in range(3):
            task_id = process_group.add_task(f"Process stage {i+1}", total=50)
            process_tasks.append(task_id)
        
        # Simulate downloads
        console.print("[cyan]Starting downloads...[/cyan]")
        for i in range(100):
            for task_id in download_tasks:
                download_group.update(task_id, advance=1)
            time.sleep(0.03)
        
        # Complete downloads
        for task_id in download_tasks:
            manager.complete_task(task_id)
        
        console.print(f"[green]Downloads complete! Group progress: {download_group.get_progress():.1f}%[/green]")
        
        # Simulate processing
        console.print("\n[cyan]Starting processing...[/cyan]")
        for i in range(50):
            for task_id in process_tasks:
                process_group.update(task_id, advance=1)
            time.sleep(0.05)
        
        # Complete processing
        for task_id in process_tasks:
            manager.complete_task(task_id)
        
        console.print(f"[green]Processing complete! Group progress: {process_group.get_progress():.1f}%[/green]")
        
    finally:
        manager.stop()


def demo_file_progress():
    """Demo file processing progress."""
    console = Console()
    
    console.print("\n[bold]File Progress Demo[/bold]\n")
    
    # Simulate files
    files = [
        "document1.pdf",
        "image.jpg", 
        "data.csv",
        "report.docx",
        "presentation.pptx"
    ]
    
    # Create progress tracker
    update_progress = create_file_progress(files, "Converting")
    
    try:
        # Process files
        for file in files:
            console.print(f"\n[cyan]Processing {file}...[/cyan]")
            
            # Simulate processing with progress updates
            for progress in range(0, 101, 10):
                update_progress(file, progress)
                time.sleep(0.1)
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted![/yellow]")


def demo_complex_scenario():
    """Demo complex progress scenario."""
    console = Console()
    
    console.print("\n[bold]Complex Progress Scenario Demo[/bold]\n")
    console.print("Simulating data pipeline with multiple stages...\n")
    
    display = MultiProgressDisplay(
        title="Data Pipeline",
        show_stats=True,
        show_timeline=True
    )
    
    display.start()
    
    try:
        # Stage 1: Download
        download_id = display.manager.create_task(
            "download",
            "Downloading dataset",
            total=500
        )
        
        for i in range(500):
            display.manager.update_task("download", advance=1)
            time.sleep(0.01)
        
        display.manager.complete_task("download")
        
        # Stage 2: Extract
        extract_id = display.manager.create_task(
            "extract",
            "Extracting files",
            total=None  # Indeterminate
        )
        
        time.sleep(2)  # Simulate extraction
        display.manager.complete_task("extract")
        
        # Stage 3: Process multiple files
        num_files = 10
        for i in range(num_files):
            task_id = f"process_{i}"
            display.manager.create_task(
                task_id,
                f"Processing file {i+1}/{num_files}",
                total=100
            )
        
        # Process files with random speeds
        active_tasks = [f"process_{i}" for i in range(num_files)]
        
        while active_tasks:
            # Update random tasks
            for task_id in active_tasks[:]:
                advance = random.randint(5, 15)
                display.manager.update_task(task_id, advance=advance)
                
                # Check completion
                task = display.manager.tasks[task_id]
                if task.current >= task.total:
                    display.manager.complete_task(task_id)
                    active_tasks.remove(task_id)
            
            time.sleep(0.1)
        
        # Stage 4: Upload results
        upload_id = display.manager.create_task(
            "upload",
            "Uploading results",
            total=200
        )
        
        for i in range(200):
            display.manager.update_task("upload", advance=1)
            time.sleep(0.02)
        
        display.manager.complete_task("upload")
        
        # Show final summary
        time.sleep(2)
        summary = display.manager.get_summary()
        
        console.print(f"\n[green]Pipeline complete![/green]")
        console.print(f"Total tasks: {summary['total']}")
        console.print(f"Completed: {summary['completed']}")
        console.print(f"Overall progress: {summary['overall_progress']:.1f}%")
        
    finally:
        display.stop()


def main():
    """Run progress management demos."""
    console = Console()
    
    demos = [
        ("Basic Progress Tracking", demo_basic_progress),
        ("Multi-Progress Display", demo_multi_progress),
        ("Progress Groups", demo_progress_groups),
        ("File Progress Helper", demo_file_progress),
        ("Complex Pipeline Scenario", demo_complex_scenario),
    ]
    
    console.print("\n[bold cyan]Progress Management Demo Suite[/bold cyan]\n")
    console.print("Explore progress tracking capabilities:\n")
    
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"{i}. {name}")
    
    console.print("\nPress Ctrl+C to exit")
    
    while True:
        try:
            choice = console.input("\nSelect demo (1-5): ")
            if choice.isdigit() and 1 <= int(choice) <= len(demos):
                _, demo_func = demos[int(choice) - 1]
                demo_func()
                console.input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()