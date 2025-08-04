"""Animation utilities for interactive CLI components."""

import time
from typing import List, Optional, Callable
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.align import Align


class MenuAnimations:
    """Animations for menu transitions and effects."""
    
    @staticmethod
    def fade_in(
        console: Console,
        content: str,
        duration: float = 0.5,
        steps: int = 10
    ) -> None:
        """Fade in animation for text.
        
        Args:
            console: Rich console
            content: Content to fade in
            duration: Animation duration
            steps: Number of fade steps
        """
        if duration <= 0:
            console.print(content)
            return
            
        delay = duration / steps
        
        # Create gradient of dimness
        for i in range(steps + 1):
            opacity = i / steps
            if opacity < 0.3:
                style = "dim"
            elif opacity < 0.7:
                style = "bright_black"
            else:
                style = ""
            
            console.clear()
            console.print(content, style=style)
            
            if i < steps:
                time.sleep(delay)
    
    @staticmethod
    def slide_in(
        console: Console,
        content: str,
        direction: str = "left",
        duration: float = 0.3
    ) -> None:
        """Slide in animation.
        
        Args:
            console: Rich console
            content: Content to slide in
            direction: Slide direction (left, right, top, bottom)
            duration: Animation duration
        """
        if duration <= 0:
            console.print(content)
            return
        
        width = console.width
        lines = content.split('\n')
        steps = 10
        delay = duration / steps
        
        if direction in ["left", "right"]:
            for i in range(steps + 1):
                console.clear()
                offset = int((1 - i / steps) * width)
                
                if direction == "left":
                    # Slide from right
                    for line in lines:
                        console.print(" " * offset + line)
                else:
                    # Slide from left
                    for line in lines:
                        if offset < width:
                            visible_width = width - offset
                            console.print(line[:visible_width])
                
                if i < steps:
                    time.sleep(delay)
        else:
            console.print(content)
    
    @staticmethod
    def typewriter(
        console: Console,
        text: str,
        delay: float = 0.03
    ) -> None:
        """Typewriter effect for text.
        
        Args:
            console: Rich console
            text: Text to type
            delay: Delay between characters
        """
        for char in text:
            console.print(char, end="")
            time.sleep(delay)
        console.print()
    
    @staticmethod
    def pulse(
        console: Console,
        content: str,
        cycles: int = 3,
        duration: float = 1.0
    ) -> None:
        """Pulse animation for emphasis.
        
        Args:
            console: Rich console
            content: Content to pulse
            cycles: Number of pulse cycles
            duration: Total duration
        """
        if duration <= 0:
            console.print(content)
            return
            
        cycle_duration = duration / cycles
        steps_per_cycle = 10
        delay = cycle_duration / steps_per_cycle
        
        for _ in range(cycles):
            # Fade in
            for i in range(steps_per_cycle // 2):
                opacity = i / (steps_per_cycle // 2)
                style = "dim" if opacity < 0.5 else ""
                console.clear()
                console.print(content, style=style)
                time.sleep(delay)
            
            # Fade out
            for i in range(steps_per_cycle // 2):
                opacity = 1 - (i / (steps_per_cycle // 2))
                style = "dim" if opacity < 0.5 else ""
                console.clear()
                console.print(content, style=style)
                time.sleep(delay)


class TransitionEffect:
    """Transition effects between menu screens."""
    
    def __init__(self, console: Console):
        """Initialize transition effect.
        
        Args:
            console: Rich console
        """
        self.console = console
    
    def wipe(
        self,
        direction: str = "left",
        duration: float = 0.2,
        char: str = "█"
    ) -> None:
        """Wipe transition effect.
        
        Args:
            direction: Wipe direction
            duration: Transition duration
            char: Character for wipe effect
        """
        if duration <= 0:
            self.console.clear()
            return
            
        width = self.console.width
        height = self.console.height or 24
        steps = 20
        delay = duration / steps
        
        if direction in ["left", "right"]:
            for i in range(steps + 1):
                self.console.clear()
                wipe_width = int((i / steps) * width)
                
                for _ in range(height):
                    if direction == "left":
                        line = char * wipe_width + " " * (width - wipe_width)
                    else:
                        line = " " * (width - wipe_width) + char * wipe_width
                    self.console.print(line, end="")
                
                time.sleep(delay)
        
        self.console.clear()
    
    def dissolve(self, duration: float = 0.3) -> None:
        """Dissolve transition effect.
        
        Args:
            duration: Transition duration
        """
        if duration <= 0:
            self.console.clear()
            return
            
        import random
        
        width = self.console.width
        height = self.console.height or 24
        total_chars = width * height
        steps = 10
        delay = duration / steps
        
        # Create random positions
        positions = [(x, y) for y in range(height) for x in range(width)]
        random.shuffle(positions)
        
        chars_per_step = total_chars // steps
        
        # Initialize screen
        screen = [[" " for _ in range(width)] for _ in range(height)]
        
        for step in range(steps):
            # Clear random positions
            start_idx = step * chars_per_step
            end_idx = min(start_idx + chars_per_step, total_chars)
            
            for i in range(start_idx, end_idx):
                if i < len(positions):
                    x, y = positions[i]
                    screen[y][x] = "."
            
            # Render screen
            self.console.clear()
            for row in screen:
                self.console.print("".join(row))
            
            time.sleep(delay)
        
        self.console.clear()


class LoadingAnimation:
    """Loading animations for async operations."""
    
    def __init__(self, console: Console):
        """Initialize loading animation.
        
        Args:
            console: Rich console
        """
        self.console = console
        self._stop = False
    
    def spinner(
        self,
        message: str = "Loading...",
        style: str = "cyan"
    ) -> None:
        """Animated spinner.
        
        Args:
            message: Loading message
            style: Message style
        """
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        with Live(
            Text(f"{frames[0]} {message}", style=style),
            console=self.console,
            refresh_per_second=10
        ) as live:
            i = 0
            while not self._stop:
                live.update(Text(f"{frames[i % len(frames)]} {message}", style=style))
                i += 1
                time.sleep(0.1)
    
    def progress_bar(
        self,
        message: str = "Processing...",
        total: int = 100,
        callback: Optional[Callable[[], int]] = None
    ) -> None:
        """Animated progress bar.
        
        Args:
            message: Progress message
            total: Total steps
            callback: Function to get current progress
        """
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(message, total=total)
            
            while not self._stop:
                if callback:
                    current = callback()
                    progress.update(task, completed=current)
                    if current >= total:
                        break
                else:
                    progress.advance(task, 1)
                    if progress.tasks[0].completed >= total:
                        break
                
                time.sleep(0.1)
    
    def stop(self) -> None:
        """Stop the animation."""
        self._stop = True


class MenuDecorations:
    """Decorative elements for menus."""
    
    @staticmethod
    def create_banner(
        title: str,
        subtitle: Optional[str] = None,
        width: Optional[int] = None,
        style: str = "bold cyan"
    ) -> Panel:
        """Create decorative banner.
        
        Args:
            title: Banner title
            subtitle: Banner subtitle
            width: Banner width
            style: Banner style
            
        Returns:
            Rich Panel with banner
        """
        content = Text(title, style=style, justify="center")
        if subtitle:
            content.append("\n")
            content.append(Text(subtitle, style="dim", justify="center"))
        
        return Panel(
            Align.center(content, vertical="middle"),
            width=width,
            border_style=style,
            padding=(1, 2)
        )
    
    @staticmethod
    def create_divider(
        text: Optional[str] = None,
        style: str = "dim",
        char: str = "─"
    ) -> str:
        """Create text divider.
        
        Args:
            text: Divider text
            style: Divider style
            char: Divider character
            
        Returns:
            Formatted divider string
        """
        if text:
            padding = 3
            side_length = 20
            divider = f"{char * side_length} {text} {char * side_length}"
        else:
            divider = char * 50
        
        return f"[{style}]{divider}[/{style}]"
    
    @staticmethod
    def create_box(
        content: str,
        title: Optional[str] = None,
        style: str = "blue",
        padding: int = 1
    ) -> Panel:
        """Create decorative box.
        
        Args:
            content: Box content
            title: Box title
            style: Box style
            padding: Internal padding
            
        Returns:
            Rich Panel box
        """
        return Panel(
            content,
            title=title,
            border_style=style,
            padding=(padding, padding * 2),
            expand=False
        )