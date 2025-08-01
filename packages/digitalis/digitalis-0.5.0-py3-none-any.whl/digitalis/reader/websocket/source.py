"""WebSocket source implementation with dynamic topic discovery."""

import asyncio
import contextlib
import json
import logging
import struct
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import websockets
from mcap.well_known import SchemaEncoding
from mcap_ros2._dynamic import DecoderFunction, generate_dynamic

from digitalis.reader.source import Source
from digitalis.reader.types import MessageEvent, SourceInfo, Topic

logger = logging.getLogger(__name__)


class OpCodes(Enum):
    """WebSocket operation codes."""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ADVERTISE = "advertise"
    UNADVERTISE = "unadvertise"
    SERVER_INFO = "serverInfo"


@dataclass
class AdvertisedChannel:
    """Information about an advertised channel."""

    id: int
    topic: str
    encoding: str
    schema_name: str
    schema: str
    schema_encoding: str


class ROS2DecodeError(Exception):
    """Raised if a message cannot be decoded as a ROS2 message."""


def get_decoder(schema: AdvertisedChannel, cache: dict[int, DecoderFunction]) -> DecoderFunction:
    """Get or create a decoder for a schema."""
    if schema is None or schema.schema_encoding != SchemaEncoding.ROS2:
        msg = f"Invalid schema for ROS2 decoding: {schema.schema_encoding}"
        raise ROS2DecodeError(msg)

    decoder = cache.get(schema.id)
    if decoder is None:
        type_dict = generate_dynamic(schema.schema_name, schema.schema)
        if schema.schema_name not in type_dict:
            raise ROS2DecodeError(f'Schema parsing failed for "{schema.schema_name}"')
        decoder = type_dict[schema.schema_name]
        cache[schema.id] = decoder
    return decoder


class WebSocketSource(Source):
    """WebSocket source for real-time data streaming with dynamic topic discovery."""

    def __init__(self, url: str, subprotocol: str = "foxglove.websocket.v1") -> None:
        self.url = url
        self.subprotocol = subprotocol

        self._ws: websockets.ClientConnection | None = None
        self._advertised_channels: dict[int, AdvertisedChannel] = {}
        self._topics: dict[str, Topic] = {}
        self._next_sub_id = 0
        self._active_subscriptions: set[int] = set()
        self._subscription_to_channel: dict[int, int] = {}
        self._channel_to_subscription: dict[int, int] = {}
        self._decoder_cache: dict[int, DecoderFunction] = {}
        self._subscribed_topics: set[str] = set()

        self._running = False
        self._play_back = True
        self._message_task: asyncio.Task | None = None

        # Callback handlers
        self._message_handler: Callable[[MessageEvent], None] | None = None
        self._source_info_handler: Callable[[SourceInfo], None] | None = None
        self._time_handler: Callable[[int], None] | None = None

    async def initialize(self) -> SourceInfo:
        """Initialize the WebSocket connection."""
        logger.info(f"Initializing WebSocket source: {self.url}")

        try:
            await self._connect()
            self._running = True
            self._message_task = asyncio.create_task(self._handle_messages_loop())
            logger.info("WebSocket source initialized")
        except Exception:
            logger.exception("Failed to initialize WebSocket source")
            self._running = False
            raise

        # Return initial empty source info - topics will be discovered dynamically
        source_info = SourceInfo(topics=[])

        # Notify source info handler
        if self._source_info_handler:
            self._source_info_handler(source_info)

        return source_info

    def start_playback(self) -> None:
        """Start or resume playback."""
        self._play_back = True

    def pause_playback(self) -> None:
        """Pause playback."""
        self._play_back = False

    async def subscribe(self, topic: str) -> None:
        """Subscribe to messages from a topic."""
        if topic in self._subscribed_topics:
            logger.debug(f"Already subscribed to topic {topic}")
            return

        self._subscribed_topics.add(topic)

        if not self._running or not self._ws:
            logger.warning("WebSocket not connected, subscription will be attempted when connected")
            return

        # Find channel for this topic
        channel_id = None
        for channel in self._advertised_channels.values():
            if channel.topic == topic:
                channel_id = channel.id
                break

        if channel_id is None:
            logger.warning(f"Topic {topic} not yet advertised by server")
            return

        await self._subscribe_to_channel(channel_id)

    async def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from messages from a topic."""
        if topic not in self._subscribed_topics:
            logger.warning(f"Not subscribed to topic {topic}")
            return

        self._subscribed_topics.remove(topic)

        # Find and unsubscribe from channel
        sub_id = None
        for channel in self._advertised_channels.values():
            if channel.topic == topic:
                sub_id = self._channel_to_subscription.get(channel.id)
                break

        if sub_id is not None:
            await self._unsubscribe_from_channel(sub_id, topic)

    def set_message_handler(self, handler: Callable[[MessageEvent], None]) -> None:
        """Set the callback for handling incoming messages."""
        self._message_handler = handler

    def set_source_info_handler(self, handler: Callable[[SourceInfo], None]) -> None:
        """Set the callback for handling source info updates."""
        self._source_info_handler = handler

    def set_time_handler(self, handler: Callable[[int], None]) -> None:
        """Set the callback for handling time updates."""
        self._time_handler = handler

    async def close(self) -> None:
        """Clean up resources and close the connection."""
        logger.info("Closing WebSocket source")

        self._running = False

        if self._message_task:
            self._message_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._message_task

        if self._ws and self._active_subscriptions:
            try:
                await self._ws.send(
                    json.dumps(
                        {
                            "op": OpCodes.UNSUBSCRIBE.value,
                            "subscriptionIds": list(self._active_subscriptions),
                        }
                    )
                )
            except (websockets.ConnectionClosed, OSError):
                logger.debug("Failed to send unsubscribe on close")

        if self._ws:
            await self._ws.close()

        logger.info("WebSocket source closed")

    async def _connect(self) -> None:
        """Establish WebSocket connection."""
        subprotocol = websockets.Subprotocol(self.subprotocol)
        self._ws = await websockets.connect(self.url, subprotocols=[subprotocol])
        logger.info(f"Connected to {self.url}")

    async def _subscribe_to_channel(self, channel_id: int) -> None:
        """Subscribe to a specific channel."""
        if not self._ws:
            logger.warning("Cannot subscribe: not connected")
            return

        sub_id = self._next_sub_id
        self._next_sub_id += 1

        msg = {
            "op": OpCodes.SUBSCRIBE.value,
            "subscriptions": [{"id": sub_id, "channelId": channel_id}],
        }

        await self._ws.send(json.dumps(msg))
        logger.info(f"Subscribed to channel {channel_id} with subscription ID {sub_id}")

        self._active_subscriptions.add(sub_id)
        self._subscription_to_channel[sub_id] = channel_id
        self._channel_to_subscription[channel_id] = sub_id

    async def _unsubscribe_from_channel(self, sub_id: int, topic: str) -> None:
        """Unsubscribe from a specific channel."""
        if not self._ws:
            logger.warning("Cannot unsubscribe: not connected")
            return

        msg = {
            "op": OpCodes.UNSUBSCRIBE.value,
            "subscriptionIds": [sub_id],
        }

        await self._ws.send(json.dumps(msg))
        logger.info(f"Unsubscribed from topic {topic} (subscription ID {sub_id})")

        # Clean up tracking
        self._active_subscriptions.discard(sub_id)
        channel_id = self._subscription_to_channel.pop(sub_id, None)
        if channel_id is not None:
            self._channel_to_subscription.pop(channel_id, None)

    async def _handle_messages_loop(self) -> None:
        """Main message handling loop."""
        if not self._ws:
            return

        try:
            async for raw in self._ws:
                if isinstance(raw, bytes):
                    await self._handle_binary(raw)
                elif isinstance(raw, str):
                    await self._handle_json(raw)
                else:
                    logger.warning(f"Received unknown message type: {type(raw)}")
        except websockets.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception:
            logger.exception("Error in message loop")
        finally:
            self._running = False

    async def _handle_json(self, text: str) -> None:
        """Handle JSON messages from the server."""
        try:
            msg = json.loads(text)
            op = msg.get("op")

            if op == OpCodes.SERVER_INFO.value:
                logger.info(f"Server info: {msg}")
            elif op == OpCodes.ADVERTISE.value:
                await self._handle_advertise(msg)
            elif op == OpCodes.UNADVERTISE.value:
                await self._handle_unadvertise(msg)
            else:
                logger.debug(f"Unknown JSON operation: {op}")
        except Exception:
            logger.exception(f"Failed to handle JSON message: {text}")

    async def _handle_advertise(self, msg: dict[str, Any]) -> None:
        """Handle topic advertisement from the server."""
        new_topics = []

        for ch in msg.get("channels", []):
            channel = AdvertisedChannel(
                id=ch["id"],
                topic=ch["topic"],
                encoding=ch["encoding"],
                schema_name=ch["schemaName"],
                schema=ch["schema"],
                schema_encoding=ch["schemaEncoding"],
            )

            self._advertised_channels[ch["id"]] = channel

            topic = Topic(
                name=ch["topic"],
                schema_name=ch["schemaName"],
                topic_id=ch["id"],
            )
            self._topics[ch["topic"]] = topic
            new_topics.append(topic)

            logger.info(f"Topic advertised: {ch['topic']} (ID: {ch['id']})")

            # Subscribe if we were waiting for this topic
            if ch["topic"] in self._subscribed_topics:
                await self._subscribe_to_channel(ch["id"])

        if new_topics:
            # Send all currently available topics
            all_topics = list(self._topics.values())

            # Update source info when topics change
            if self._source_info_handler:
                source_info = SourceInfo(topics=all_topics)
                self._source_info_handler(source_info)

    async def _handle_unadvertise(self, msg: dict[str, Any]) -> None:
        """Handle topic unadvertisement from the server."""
        for channel_id in msg.get("channelIds", []):
            channel = self._advertised_channels.pop(channel_id, None)
            if channel:
                self._topics.pop(channel.topic, None)
                logger.info(f"Topic unadvertised: {channel.topic}")

    async def _handle_binary(self, data: bytes) -> None:
        """Handle binary message data."""
        if not self._message_handler:
            return

        if not self._play_back:
            # If playback is paused, ignore incoming messages
            return

        opcode = data[0]
        if opcode == 0x01:  # Message Data
            sub_id = struct.unpack_from("<I", data, 1)[0]
            timestamp = struct.unpack_from("<Q", data, 5)[0]
            payload = data[1 + 4 + 8 :]

            # Get the channel for this subscription
            channel_id = self._subscription_to_channel.get(sub_id)
            if channel_id is None:
                logger.warning(f"No channel mapping for subscription {sub_id}")
                return

            channel = self._advertised_channels.get(channel_id)
            if channel is None:
                logger.warning(f"No channel info for channel {channel_id}")
                return

            # Decode message
            message_obj: Any = payload
            try:
                decoder = get_decoder(channel, self._decoder_cache)
                message_obj = decoder(payload)
            except (ROS2DecodeError, ValueError):
                logger.debug(f"Failed to decode message for topic {channel.topic}")

            # Create message event
            message_event = MessageEvent(
                topic=channel.topic,
                message=message_obj,
                timestamp_ns=timestamp,
                schema_name=channel.schema_name,
            )

            self._message_handler(message_event)

            # Notify time handler with message timestamp
            if self._time_handler:
                self._time_handler(timestamp)
        else:
            logger.debug(f"Unknown binary opcode: {opcode}")
