"""Inter-agent communication message format."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List
import time


class MessageType(Enum):
    """Message types for inter-agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    FEEDBACK = "feedback"
    HEARTBEAT = "heartbeat"
    TERMINATE = "terminate"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Message:
    """
    Structured message format for inter-agent communication.

    Attributes:
        sender: Source agent name
        receiver: Target agent name (or "ALL" for broadcast)
        content: Message payload
        msg_type: Type of message
        priority: Message priority
        timestamp: Creation time
        conversation_id: For tracking multi-message conversations
        reply_to: Original message ID if this is a reply
    """
    sender: str
    receiver: str
    content: Dict[str, Any]
    msg_type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    conversation_id: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None

    def __post_init__(self):
        if self.message_id is None:
            self.message_id = f"{self.sender}_{int(self.timestamp * 1000)}"
        if self.conversation_id is None:
            self.conversation_id = self.message_id

    @property
    def is_broadcast(self) -> bool:
        """Check if message is broadcast to all agents."""
        return self.receiver == "ALL"

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "msg_type": self.msg_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id,
            "reply_to": self.reply_to,
        }


class MessageQueue:
    """
    Thread-safe message queue for inter-agent communication.

    Features:
    - Async message passing
    - Priority-based message retrieval
    - Message filtering by sender/receiver
    - Conversation tracking
    """

    def __init__(self):
        self._messages: List[Message] = []
        self._callbacks: Dict[str, List[callable]] = {}
        self._lock = None  # Simplified for demo; use asyncio.Lock in production

    def put(self, message: Message) -> None:
        """Add a message to the queue."""
        self._messages.append(message)
        self._notify_listeners(message)

    def get(self, receiver: str, blocking: bool = False, timeout: float = None) -> Optional[Message]:
        """
        Get message for specific receiver.

        Args:
            receiver: Agent name to receive message
            blocking: Wait for message if queue is empty
            timeout: Max wait time in seconds

        Returns:
            Message if available, None otherwise
        """
        for i, msg in enumerate(self._messages):
            if msg.receiver == receiver or msg.is_broadcast:
                return self._messages.pop(i)
        return None

    def get_all_for(self, receiver: str) -> List[Message]:
        """Get all messages for a specific receiver without removing."""
        return [msg for msg in self._messages
                if msg.receiver == receiver or msg.is_broadcast]

    def peek(self, receiver: str) -> Optional[Message]:
        """Peek at next message without removing it."""
        for msg in self._messages:
            if msg.receiver == receiver or msg.is_broadcast:
                return msg
        return None

    def reply_to(self, original: Message, content: Dict[str, Any],
                 sender: str) -> Message:
        """
        Create a reply message to an original message.

        Args:
            original: Original message to reply to
            content: Reply content
            sender: Name of replying agent

        Returns:
            New reply message
        """
        return Message(
            sender=sender,
            receiver=original.sender,
            content=content,
            msg_type=MessageType.RESPONSE,
            conversation_id=original.conversation_id,
            reply_to=original.message_id,
        )

    def subscribe(self, agent_name: str, callback: callable) -> None:
        """Subscribe to messages for an agent."""
        if agent_name not in self._callbacks:
            self._callbacks[agent_name] = []
        self._callbacks[agent_name].append(callback)

    def _notify_listeners(self, message: Message) -> None:
        """Notify registered callbacks of new message."""
        if message.receiver in self._callbacks:
            for callback in self._callbacks[message.receiver]:
                callback(message)
        if message.is_broadcast:
            for agent_name, callbacks in self._callbacks.items():
                for callback in callbacks:
                    callback(message)

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()

    def size(self) -> int:
        """Get number of pending messages."""
        return len(self._messages)

    def get_conversation(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation."""
        return [msg for msg in self._messages
                if msg.conversation_id == conversation_id]

    def __len__(self) -> int:
        return len(self._messages)
