"""FFmpeg-only final composition for a sequential two-character conversation."""

from .composer import compose_conversation, build_conversation_command

__all__ = ["build_conversation_command", "compose_conversation"]
