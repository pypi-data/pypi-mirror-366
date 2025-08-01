import math
from datetime import datetime
from typing import Any, ClassVar

from rich.highlighter import ISO8601Highlighter, ReprHighlighter
from rich.text import Text
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.validation import ValidationResult, Validator
from textual.widgets import Input, Tree
from textual.widgets.tree import TreeNode

from digitalis.grammar import ParsedMessagePath, parse_message_path
from digitalis.grammar.query import QueryError, apply_query
from digitalis.reader.types import MessageEvent
from digitalis.ui.panels.base import SCHEMA_ANY, BasePanel
from digitalis.utilities import NANOSECONDS_PER_SECOND, STRFTIME_FORMAT, nanoseconds_to_iso


def _quaternion_to_euler(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    """Convert quaternion to Euler angles."""

    # Convert quaternion to Euler angles (roll, pitch, yaw)
    # TODO: is this correct?
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = min(t2, +1.0)
    t2 = max(t2, -1.0)
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z


highlighter = ReprHighlighter()
iso_highlighter = ISO8601Highlighter()


def add_node(name: str, node: TreeNode, obj: Any, expand_depth: int) -> None:  # noqa: PLR0912
    """Adds a node to the tree.

    Args:
        name (str): Name of the node.
        node (TreeNode): Parent node.
        data (object): Data associated with the node.
    """
    if not hasattr(obj, "__slots__"):
        node.allow_expand = False
        if isinstance(obj, bytes):
            # only show the first 100 bytes of bytes objects
            start_bytes = obj[:100]
            obj_repr = f"bytes({len(obj)}): {start_bytes!r}..."
        else:
            obj_repr = repr(obj)
        if name:
            label = Text.assemble(Text.from_markup(f"[b]{name}[/b]="), highlighter(obj_repr))
        else:
            label = Text(obj_repr)
        node.set_label(label)
        return

    if obj.__slots__ == ["sec", "nanosec"]:
        # Convert timestamp to ISO format
        timestamp = iso_highlighter(
            datetime.fromtimestamp(obj.sec + obj.nanosec / NANOSECONDS_PER_SECOND).strftime(
                STRFTIME_FORMAT
            )
        )
        stamp_label = Text.assemble(Text.from_markup(f"[b]{name}[/b]="), timestamp)
        node.set_label(stamp_label)
    elif obj.__slots__ == ["x", "y", "z", "w"]:
        # convert quaternion to Euler angles
        roll, pitch, yaw = _quaternion_to_euler(obj.x, obj.y, obj.z, obj.w)
        euler_label = Text.assemble(
            Text.from_markup(f"[b]{name}[/b]="),
            highlighter(f"r={roll:.2f}, p={pitch:.2f}, y={yaw:.2f}"),
        )
        node.set_label(euler_label)
    elif expand_depth >= 0:
        node.expand()

    for slot in obj.__slots__:
        data = getattr(obj, slot)
        child = node.add(slot)
        if isinstance(data, (list, tuple)):
            child.set_label(Text(f"{slot}[{len(data)}]"))
            for index, value in enumerate(data):
                new_node = child.add(f"[{index}]")
                if expand_depth >= 0:
                    new_node.expand()
                add_node(str(index), new_node, value, expand_depth - 1)
                if index > 25:  # TODO: lazy load these?
                    add_node("Truncated", new_node, "...", expand_depth - 1)
                    break
        else:
            add_node(slot, child, data, expand_depth - 1)


class QueryValidator(Validator):
    """Validator for query syntax using parse_message_path."""

    def __init__(self) -> None:
        super().__init__()
        self._cached_parsed: ParsedMessagePath | None = None
        self._cached_query: str = ""

    def validate(self, value: str) -> ValidationResult:
        """Validate query syntax and cache parsed result.

        Args:
            value: The query string to validate

        Returns:
            ValidationResult indicating success or failure
        """
        if not value.strip():
            self._cached_parsed = None
            self._cached_query = value
            return self.success()

        try:
            parsed = parse_message_path(f"/dummy{value}")
            self._cached_parsed = parsed
            self._cached_query = value
            return self.success()
        except ValueError as e:
            self._cached_parsed = None
            self._cached_query = value
            return self.failure(f"Invalid query syntax: {e}")

    def get_cached_parsed(self, query: str) -> ParsedMessagePath | None:
        """Get cached parsed result if query matches.

        Args:
            query: The query string to check

        Returns:
            Cached parsed result or None if not available
        """
        if query == self._cached_query:
            return self._cached_parsed
        return None


class TreeView(Tree):
    data: reactive[MessageEvent | None] = reactive(None)

    def watch_data(self, channel_message: MessageEvent | None) -> None:
        """Adds data from MessageEvent to a node.

        Args:
            channel_message: MessageEvent containing schema, timestamp, and message data.
        """
        if not channel_message:
            return

        self.clear()

        # Add dummy item showing schema @ timestamp
        timestamp = nanoseconds_to_iso(channel_message.timestamp_ns)
        timestamp = iso_highlighter(timestamp)
        schema_name = "n/a"
        if channel_message.schema_name:
            schema_name = channel_message.schema_name

        dummy_label = Text.assemble(
            Text.from_markup(f"[bold]{schema_name}[/bold] @ "),
            timestamp,
        )
        msg_type_time_node = self.root.add("")
        msg_type_time_node.set_label(dummy_label)
        msg_type_time_node.allow_expand = False

        # Handle case where filtered result is a primitive
        if not hasattr(channel_message.message, "__slots__"):
            # If the message is a primitive, add it directly as a labeled node
            primitive_node = self.root.add("")
            label = highlighter(repr(channel_message.message))
            primitive_node.set_label(label)
            primitive_node.allow_expand = False
        else:
            add_node("root", self.root, channel_message.message, 3)


class Raw(BasePanel):
    SUPPORTED_SCHEMAS: ClassVar[set[str]] = {SCHEMA_ANY}
    PRIORITY: ClassVar[int] = 1000  # Should be the last panel

    parsed_query: reactive[ParsedMessagePath | None] = reactive(None)

    def __init__(self) -> None:
        super().__init__()
        self._validator = QueryValidator()

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Input(placeholder="Filter", compact=True, validators=[self._validator])
        yield TreeView("root").data_bind(guide_depth=2, show_root=False)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle query changes from Input."""
        if event.validation_result and event.validation_result.is_valid:
            self.parsed_query = self._validator.get_cached_parsed(event.value)
            self._update_date()

    def _update_date(self) -> None:
        tree = self.query_one(TreeView)

        if self.parsed_query and self.data and self.parsed_query:
            try:
                filtered_message = apply_query(self.parsed_query, self.data.message)
                tree.data = MessageEvent(
                    topic=self.data.topic,
                    message=filtered_message,
                    timestamp_ns=self.data.timestamp_ns,
                    schema_name=self.data.schema_name,
                )
            except QueryError:
                # Ignore for now
                pass
        else:
            tree.data = self.data

    def watch_data(self, _data: MessageEvent | None) -> None:
        self._update_date()
