"""Reusable data model for sequential character conversations."""

from .models import FLOAT_EMOTIONS, ConversationTimeline, DialogueTurn
from .timeline import build_timeline, calculate_total_duration, create_turn, validate_timeline

__all__ = [
    "FLOAT_EMOTIONS",
    "ConversationTimeline",
    "DialogueTurn",
    "build_timeline",
    "calculate_total_duration",
    "create_turn",
    "validate_timeline",
]
