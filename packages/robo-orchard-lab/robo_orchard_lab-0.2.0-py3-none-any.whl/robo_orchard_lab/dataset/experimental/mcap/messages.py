# Project RoboOrchard
#
# Copyright (c) 2024-2025 Horizon Robotics. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations
from bisect import bisect_left
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterator,
    Literal,
    Optional,
    TypeVar,
)

from mcap.records import (
    Channel as McapChannel,
    Message as McapMessage,
    Schema as McapSchema,
)

if TYPE_CHECKING:
    from robo_orchard_lab.dataset.experimental.mcap.msg_decoder import (
        McapDecoderContext,
    )


__all__ = [
    "StampedMessage",
    "McapMessageTuple",
    "McapDecodedMessageTuple",
    "McapMessagesTuple",
]


T = TypeVar("T", bound=Any)


@dataclass
class StampedMessage(Generic[T]):
    """Any message with timestamp."""

    data: T
    """The actual message data."""
    log_time: int | None
    """The log time in nanoseconds."""
    pub_time: int | None
    """The publish time in nanoseconds."""


@dataclass
class McapMessageTuple:
    schema: Optional[McapSchema]
    channel: McapChannel
    message: McapMessage

    def decode(self, decoder_ctx: McapDecoderContext) -> Any:
        """Decode the message using the provided decoder context."""
        return decoder_ctx.decode_message(
            message_encoding=self.channel.message_encoding,
            message=self.message,
            schema=self.schema,
        )


@dataclass
class McapDecodedMessageTuple(McapMessageTuple):
    decoded_message: Any

    def decode(self, decoder_ctx: McapDecoderContext) -> Any:
        """Return the already decoded message.

        If not decoded, decode it.
        """
        if self.decoded_message is None:
            self.decoded_message = decoder_ctx.decode_message(
                message_encoding=self.channel.message_encoding,
                message=self.message,
                schema=self.schema,
            )
        return self.decoded_message


@dataclass
class McapMessagesTuple:
    schema: Optional[McapSchema]
    channel: McapChannel
    messages: list[McapMessage]

    @property
    def min_log_time(self) -> int:
        """Return the minimum log time of all messages."""
        if not self.messages:
            raise ValueError("No messages in the tuple.")
        return min(msg.log_time for msg in self.messages)

    @property
    def max_log_time(self) -> int:
        """Return the maximum log time of all messages."""
        if not self.messages:
            raise ValueError("No messages in the tuple.")
        return max(msg.log_time for msg in self.messages)

    def split(
        self,
        log_time: int,
        is_sorted_asc: bool = False,
    ) -> tuple[McapMessagesTuple | None, McapMessagesTuple | None]:
        """Split the messages tuple into two parts based on the log time.

        This method returns two new `McapMessagesTuple` instances:
        - The first contains messages with `log_time < log_time`.
        - The second contains messages with `log_time >= log_time`.

        Args:
            log_time (int): The log time to split the messages.
            is_sorted_asc (bool, optional): Whether the messages are already
                sorted in ascending order by log time. If True, a binary search
                will be used to find the split point. Defaults to False.

        """
        left = []
        right = []
        if not is_sorted_asc:
            for msg in self.messages:
                if msg.log_time < log_time:
                    left.append(msg)
                else:
                    right.append(msg)
        else:
            # If the messages are already sorted ascending by log_time,
            # we can use binary search to find the split point.
            idx = bisect_left(
                self.messages, log_time, key=lambda msg: msg.log_time
            )
            left = self.messages[:idx]
            right = self.messages[idx:]

        ret_left = (
            McapMessagesTuple(
                schema=self.schema, channel=self.channel, messages=left
            )
            if len(left) > 0
            else None
        )
        ret_right = (
            McapMessagesTuple(
                schema=self.schema, channel=self.channel, messages=right
            )
            if len(right) > 0
            else None
        )

        return (ret_left, ret_right)

    def sort(
        self,
        key: Literal["log_time", "publish_time"] = "log_time",
        reverse: bool = False,
    ) -> None:
        """Sort the messages by log time."""
        if key == "log_time":
            # Sort by log_time, which is an attribute of McapMessage
            self.messages.sort(key=lambda msg: msg.log_time, reverse=reverse)
        elif key == "publish_time":
            # Sort by pub_time, which is an attribute of McapMessage
            self.messages.sort(
                key=lambda msg: msg.publish_time, reverse=reverse
            )
        else:
            raise ValueError(
                f"Invalid sort key: {key}. Use 'log_time' or 'pub_time'."
            )

    def __iter__(self) -> Iterator[McapMessage]:
        """Return an iterator over the messages in the tuple."""
        return iter(self.messages)

    def __getitem__(self, index: int) -> McapMessage:
        return self.messages[index]

    def __len__(self) -> int:
        """Return the number of messages in the tuple."""
        return len(self.messages)

    def append(self, msg: McapMessage | McapMessageTuple) -> None:
        """Append a new message to the messages tuple."""

        if isinstance(msg, McapMessage):
            self.messages.append(msg)
        elif isinstance(msg, McapMessageTuple):
            # check if the channel matches
            if self.channel.topic != msg.channel.topic:
                raise ValueError(
                    f"Channel mismatch: {self.channel.topic} != {msg.channel.topic}"  # noqa: E501
                )
            self.messages.append(msg.message)
        else:
            raise TypeError(
                "msg must be an instance of McapMessage or McapMessageTuple"
            )

    def decode(self, decoder_ctx: McapDecoderContext) -> list[Any]:
        """Decode all messages in the tuple using the provided decoder context."""  # noqa: E501
        decoded_messages = []
        for msg in self.messages:
            decoded_message = decoder_ctx.decode_message(
                message_encoding=self.channel.message_encoding,
                message=msg,
                schema=self.schema,
            )
            decoded_messages.append(decoded_message)
        return decoded_messages
