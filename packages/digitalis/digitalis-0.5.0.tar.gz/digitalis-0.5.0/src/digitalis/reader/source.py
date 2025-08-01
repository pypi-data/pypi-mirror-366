"""Core source interfaces for data access and playback control."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from .types import MessageEvent, SourceInfo


class Source(ABC):
    """Base interface for data sources that provide topic subscription and message delivery."""

    @abstractmethod
    async def initialize(self) -> SourceInfo:
        """Initialize the source and return available topics and metadata."""
        ...

    @abstractmethod
    def start_playback(self) -> None:
        """Start or resume playback."""
        ...

    @abstractmethod
    def pause_playback(self) -> None:
        """Pause playback."""
        ...

    @abstractmethod
    async def subscribe(self, topic: str) -> None:
        """Subscribe to messages from a topic."""
        ...

    @abstractmethod
    async def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from messages from a topic."""
        ...

    @abstractmethod
    def set_message_handler(self, handler: Callable[[MessageEvent], None]) -> None:
        """Set callback to handle incoming messages."""
        ...

    @abstractmethod
    def set_source_info_handler(self, handler: Callable[[SourceInfo], None]) -> None:
        """Set callback to handle source info updates (time range, metadata changes)."""
        ...

    @abstractmethod
    def set_time_handler(self, handler: Callable[[int], None]) -> None:
        """Set callback to handle time updates."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources and close the source."""
        ...


class PlaybackSource(Source):
    """Extended interface for sources that support playback control (e.g., file-based sources)."""

    @abstractmethod
    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed multiplier (1.0 = normal speed, 2.0 = 2x speed, etc.)."""
        ...

    @abstractmethod
    async def seek_to_time(self, timestamp_ns: int) -> None:
        """Seek to a specific timestamp in nanoseconds."""
        ...

    @property
    @abstractmethod
    def is_playing(self) -> bool:
        """Return True if playback is currently active."""
        ...

    @property
    @abstractmethod
    def time_range(self) -> tuple[int, int] | None:
        """Return (start_time_ns, end_time_ns) tuple, or None if not available."""
        ...

    @property
    @abstractmethod
    def current_time(self) -> int | None:
        """Return current playback time in nanoseconds, or None if not available."""
        ...
