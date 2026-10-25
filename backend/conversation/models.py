"""Data structures used by the conversation timeline engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


FLOAT_EMOTIONS = frozenset({"none", "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"})


@dataclass(frozen=True)
class DialogueTurn:
    """One ordered spoken turn in a conversation.

    ``start_time`` may be ``None`` before a timeline is built.  A completed
    ``ConversationTimeline`` always contains concrete, non-overlapping starts.
    """

    character_id: str
    character_name: str
    dialogue: str
    emotion: str
    emotion_strength: float
    duration: float
    start_time: Optional[float] = None


@dataclass(frozen=True)
class ConversationTimeline:
    """A validated sequence of dialogue turns and its total duration."""

    turns: Tuple[DialogueTurn, ...]
    total_duration: float
