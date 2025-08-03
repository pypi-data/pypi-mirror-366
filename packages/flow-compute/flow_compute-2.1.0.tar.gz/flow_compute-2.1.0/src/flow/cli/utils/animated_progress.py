"""Animated progress indicators for CLI operations.

This module provides custom progress indicators with animated text,
specifically supporting dynamic ellipsis animations for status messages.
"""

import threading
import time
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.text import Text

from .animations import animation_engine
from .animation_config import AnimationStyle, get_animation_style, get_animation_config


class AnimatedEllipsisProgress:
    """Progress indicator with spinner and animated ellipsis.

    Creates a progress bar with rich's spinner and a message with
    cycling ellipsis animation (., .., ...).
    """

    def __init__(
        self,
        console: Console,
        message: str,
        transient: bool = True,
        animation_style: Optional[AnimationStyle] = None,
        start_immediately: bool = False,
    ):
        """Initialize animated progress.

        Args:
            console: Rich console instance
            message: Base message to display (without ellipsis)
            transient: Whether to clear progress when done
            animation_style: Type of text animation to use
            start_immediately: If True, start animation in __init__ for immediate feedback
        """
        self.console = console
        self.base_message = message
        self.transient = transient
        # Use centralized animation selection
        self.animation_style = get_animation_style(animation_style)
        self.animation_config = get_animation_config(self.animation_style)
        self._live: Optional[Live] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._ellipsis_count = 0
        # Reset animation engine's start time for fresh animations
        animation_engine.start_time = time.time()
        self._active = False
        self._started_immediately = False

        # Start immediately if requested - provides instant feedback
        if start_immediately:
            self._start_immediate()

    def _animate(self) -> None:
        """Animation loop for updating display."""
        spinner_frames = animation_engine.SPINNERS["dots"]

        while not self._stop_event.is_set():
            if self.animation_style == "ellipsis":
                # Classic ellipsis animation
                self._ellipsis_count = (self._ellipsis_count % 3) + 1
                dots = "." * self._ellipsis_count

                # Get spinner frame
                spinner_phase = animation_engine.get_phase(0.8)
                spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

                display = Text(f"{spinner} {self.base_message}{dots}")
            else:
                # Use rich animations - same as flow animations command
                phase = animation_engine.get_phase(duration=self.animation_config.duration)

                if self.animation_style == "wave":
                    animated_text = animation_engine.wave_pattern(
                        self.base_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "pulse":
                    animated_text = animation_engine.pulse_effect(
                        self.base_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "shimmer":
                    animated_text = animation_engine.shimmer_effect(
                        self.base_message, phase, intensity=self.animation_config.intensity
                    )
                elif self.animation_style == "bounce":
                    animated_text = animation_engine.bounce_effect(
                        self.base_message, phase, intensity=self.animation_config.intensity
                    )
                else:
                    animated_text = Text(self.base_message)

                # Get spinner frame
                spinner_phase = animation_engine.get_phase(0.8)
                spinner = animation_engine.get_spinner_frame(spinner_frames, spinner_phase)

                # Display spinner + animated text (exactly like flow animations)
                display = Text(f"{spinner} ") + animated_text

            if self._live and self._active:
                self._live.update(display)

            time.sleep(0.05)

    def _start_immediate(self):
        """Start animation immediately for instant feedback."""
        try:
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                return
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        self._started_immediately = True

    def __enter__(self):
        """Start the animated display."""
        if self._started_immediately:
            # Already started, just return
            return self

        try:
            self._live = Live(
                Text(""),  # Initial empty display
                console=self.console,
                refresh_per_second=20,
                transient=self.transient,
            )
            self._live.__enter__()
        except Exception as e:
            if "Only one live display may be active" in str(e):
                # There's already a Live display active, skip animation
                self._live = None
                self._active = False
                return self
            raise

        if self._live:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
            self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animated display."""
        if not self._active:
            return  # Already stopped

        self._active = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)

    def update_message(self, new_message: str):
        """Update the progress message while animation is running.

        Args:
            new_message: New message to display
        """
        self.base_message = new_message
