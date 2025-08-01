"""MCAP source implementation with playback control."""

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable

from digitalis.exceptions import InvalidFileFormatError
from digitalis.reader.source import PlaybackSource
from digitalis.reader.types import MessageEvent, SourceInfo, Topic

from .mcap_read_preloading import McapReaderPreloading

logger = logging.getLogger(__name__)


class McapSource(PlaybackSource):
    """MCAP file source with playback control and seeking capabilities."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._mcap_reader: McapReaderPreloading | None = None
        self._stats = None
        self._channels: dict[int, Topic] = {}
        self._subscribed_topics: set[str] = set()
        self._current_time: int | None = None
        self._playback_speed = 1.0
        self._playback_task: asyncio.Task | None = None
        self._playback_condition = asyncio.Event()

        # Callback handlers
        self._message_handler: Callable[[MessageEvent], None] | None = None
        self._source_info_handler: Callable[[SourceInfo], None] | None = None
        self._time_handler: Callable[[int], None] | None = None

    async def initialize(self) -> SourceInfo:
        """Initialize the MCAP reader and extract metadata."""
        logger.info(f"Initializing MCAP source: {self.path}")

        self._mcap_reader = McapReaderPreloading(self.path)

        summary = self._mcap_reader.summary
        stats = summary.statistics
        if stats is None:
            raise InvalidFileFormatError("Statistics not found in MCAP file")
        self._stats = stats

        topics = []

        for channel in summary.channels.values():
            schema = summary.schemas.get(channel.schema_id)
            topic = Topic(
                name=channel.topic,
                schema_name=schema.name if schema else "unknown",  # TODO: make None
                message_count=stats.channel_message_counts.get(channel.id, 0),  # TODO: make None
                topic_id=channel.id,
            )
            topics.append(topic)
            self._channels[channel.id] = topic

        self._current_time = stats.message_start_time

        self._playback_task = asyncio.create_task(self._playback_loop())

        source_info = SourceInfo(
            topics=topics,
            start_time_ns=stats.message_start_time,
            end_time_ns=stats.message_end_time,
        )

        # Notify source info handler
        if self._source_info_handler:
            self._source_info_handler(source_info)

        return source_info

    async def subscribe(self, topic: str) -> None:
        """Subscribe to messages from a topic."""
        if topic not in {t.name for t in self._channels.values()}:
            logger.warning(f"Topic {topic} not found in MCAP file")
            return

        if topic in self._subscribed_topics:
            logger.debug(f"Already subscribed to topic {topic}")
            return

        self._subscribed_topics.add(topic)
        logger.info(f"Subscribed to topic {topic}")

        # # Send current message if available
        # self._send_current_messages()
        assert self._mcap_reader is not None, "McapReader not initialized"
        self._mcap_reader.set_subscription(list(self._subscribed_topics))

    async def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from messages from a topic."""
        if topic not in self._subscribed_topics:
            logger.warning(f"Not subscribed to topic {topic}")
            return

        self._subscribed_topics.remove(topic)
        logger.info(f"Unsubscribed from topic {topic}")
        assert self._mcap_reader is not None, "McapReader not initialized"
        self._mcap_reader.set_subscription(list(self._subscribed_topics))

    def set_message_handler(self, handler: Callable[[MessageEvent], None]) -> None:
        """Set the callback for handling incoming messages."""
        self._message_handler = handler

    def set_source_info_handler(self, handler: Callable[[SourceInfo], None]) -> None:
        """Set the callback for handling source info updates."""
        self._source_info_handler = handler

    def set_time_handler(self, handler: Callable[[int], None]) -> None:
        """Set the callback for handling time updates."""
        self._time_handler = handler

    def start_playback(self) -> None:
        """Start or resume playback."""
        self._playback_condition.set()

    def pause_playback(self) -> None:
        """Pause playback."""
        self._playback_condition.clear()

    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed multiplier."""
        self._playback_speed = speed

    async def seek_to_time(self, timestamp_ns: int) -> None:
        """Seek to a specific timestamp."""
        if not self._stats:
            logger.warning("Cannot seek: not initialized")
            return

        # Clamp timestamp to valid range
        timestamp_ns = max(
            self._stats.message_start_time, min(timestamp_ns, self._stats.message_end_time)
        )

        self._current_time = timestamp_ns
        assert self._mcap_reader is not None, "McapReader not initialized"
        self._mcap_reader.seek_to_ns(timestamp_ns)

    @property
    def is_playing(self) -> bool:
        """Return True if playback is currently active."""
        return self._playback_condition.is_set()

    @property
    def time_range(self) -> tuple[int, int] | None:
        """Return the start and end time of the messages."""
        if not self._stats:
            return None
        return self._stats.message_start_time, self._stats.message_end_time

    @property
    def current_time(self) -> int | None:
        """Return current playback time."""
        return self._current_time

    async def close(self) -> None:
        """Clean up resources."""
        if self._playback_task:
            self.pause_playback()
            self._playback_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._playback_task
        logger.info("MCAP source closed")

    async def _playback_loop(self) -> None:
        """Main playback loop."""
        if not self._stats:
            return

        assert self._mcap_reader is not None, "McapReader not initialized"

        last_msg_time = None
        start = time.perf_counter_ns()

        while True:
            await self._playback_condition.wait()

            msg = self._mcap_reader.get_next_message()
            if msg is None:
                await asyncio.sleep(0)
                continue

            if self._message_handler and msg.topic in self._subscribed_topics:
                self._message_handler(msg)

            sleep_time = 0
            if last_msg_time is not None:
                msg_delta = msg.timestamp_ns - last_msg_time
                duration = time.perf_counter_ns() - start
                sleep_time = (msg_delta / self._playback_speed) - duration
                sleep_time = max(sleep_time, 0)

            # Sleep in 100ms chunks, sending time updates for smooth progression
            remaining_sleep = sleep_time / 1_000_000_000
            while remaining_sleep > 0.1:  # 100ms
                await asyncio.sleep(0.1)
                if self._time_handler and self._current_time:
                    # Advance time by 100ms worth of playback time
                    time_increment = int(0.1 * 1_000_000_000 * self._playback_speed)
                    self._current_time += time_increment
                    self._time_handler(self._current_time)
                remaining_sleep -= 0.1

            if remaining_sleep > 0:
                await asyncio.sleep(remaining_sleep)

            last_msg_time = msg.timestamp_ns
            self._current_time = msg.timestamp_ns
            if self._time_handler:
                self._time_handler(msg.timestamp_ns)
            start = time.perf_counter_ns()
