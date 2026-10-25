"""Construction and validation helpers for a sequential conversation."""

from __future__ import annotations

from dataclasses import replace
from numbers import Real
from typing import Iterable

from .models import FLOAT_EMOTIONS, ConversationTimeline, DialogueTurn


_TIME_TOLERANCE = 1e-9


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()


def _require_positive_number(value: Real, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or float(value) <= 0:
        raise ValueError(f"{field_name} must be numeric and greater than 0.")
    return float(value)


def create_turn(
    character_id: str,
    character_name: str,
    dialogue: str,
    emotion: str,
    emotion_strength: Real,
    duration: Real,
    start_time: Real | None = None,
) -> DialogueTurn:
    """Create one validated turn; omit ``start_time`` to auto-place it later."""
    normalized_emotion = _require_text(emotion, "emotion").lower()
    if normalized_emotion not in FLOAT_EMOTIONS:
        allowed = ", ".join(sorted(FLOAT_EMOTIONS))
        raise ValueError(f"emotion must be one of: {allowed}.")
    if start_time is not None:
        if isinstance(start_time, bool) or not isinstance(start_time, Real) or float(start_time) < 0:
            raise ValueError("start_time must be numeric and greater than or equal to 0.")
        start_time = float(start_time)
    return DialogueTurn(
        character_id=_require_text(character_id, "character_id"),
        character_name=_require_text(character_name, "character_name"),
        dialogue=_require_text(dialogue, "dialogue"),
        emotion=normalized_emotion,
        emotion_strength=_require_positive_number(emotion_strength, "emotion_strength"),
        duration=_require_positive_number(duration, "duration"),
        start_time=start_time,
    )


def build_timeline(turns: Iterable[DialogueTurn]) -> ConversationTimeline:
    """Return a strictly sequential timeline, filling omitted start times.

    Explicit start times are accepted only when they equal the end of the
    previous turn, which prevents both gaps and overlaps in this basic model.
    """
    completed_turns: list[DialogueTurn] = []
    next_start = 0.0
    for index, turn in enumerate(turns, start=1):
        # Revalidate, including turns supplied directly instead of via
        # create_turn(), while preserving their optional start time.
        checked = create_turn(
            turn.character_id,
            turn.character_name,
            turn.dialogue,
            turn.emotion,
            turn.emotion_strength,
            turn.duration,
            turn.start_time,
        )
        actual_start = next_start if checked.start_time is None else checked.start_time
        if abs(actual_start - next_start) > _TIME_TOLERANCE:
            relation = "overlaps a previous turn" if actual_start < next_start else "is out of sequential order"
            raise ValueError(f"Turn {index} start_time {relation}; expected {next_start:g}.")
        completed = replace(checked, start_time=next_start)
        completed_turns.append(completed)
        next_start += completed.duration

    timeline = ConversationTimeline(turns=tuple(completed_turns), total_duration=next_start)
    validate_timeline(timeline)
    return timeline


def calculate_total_duration(timeline: ConversationTimeline) -> float:
    """Validate and return the end time of the final conversation turn."""
    validate_timeline(timeline)
    return timeline.total_duration


def validate_timeline(timeline: ConversationTimeline) -> None:
    """Ensure a completed timeline is ordered, contiguous, and non-overlapping."""
    if not isinstance(timeline, ConversationTimeline):
        raise ValueError("timeline must be a ConversationTimeline instance.")
    expected_start = 0.0
    for index, turn in enumerate(timeline.turns, start=1):
        checked = create_turn(
            turn.character_id,
            turn.character_name,
            turn.dialogue,
            turn.emotion,
            turn.emotion_strength,
            turn.duration,
            turn.start_time,
        )
        if checked.start_time is None:
            raise ValueError(f"Turn {index} is missing start_time.")
        if abs(checked.start_time - expected_start) > _TIME_TOLERANCE:
            relation = "overlaps a previous turn" if checked.start_time < expected_start else "is not sequential"
            raise ValueError(f"Turn {index} {relation}; expected start_time {expected_start:g}.")
        expected_start += checked.duration
    if abs(timeline.total_duration - expected_start) > _TIME_TOLERANCE:
        raise ValueError(f"total_duration must equal {expected_start:g}.")
