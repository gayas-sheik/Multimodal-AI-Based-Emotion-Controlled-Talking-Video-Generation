"""Standalone validation test for the conversation timeline engine."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.conversation import build_timeline, calculate_total_duration, create_turn, validate_timeline


def expect_value_error(label: str, callback) -> None:
    try:
        callback()
    except ValueError as error:
        print(f"Validated invalid case ({label}): {error}")
        return
    raise AssertionError(f"Expected ValueError for {label}.")


def main() -> int:
    timeline = build_timeline([
        create_turn("alice", "Alice", "Hello Bob, how are you?", "happy", 1.0, 3),
        create_turn("bob", "Bob", "I'm fine, Alice. How are you?", "neutral", 1.0, 3),
        create_turn("alice", "Alice", "I'm doing great!", "happy", 1.0, 2),
    ])

    expected = [
        ("alice", "Alice", "Hello Bob, how are you?", "happy", 1.0, 0.0, 3.0),
        ("bob", "Bob", "I'm fine, Alice. How are you?", "neutral", 1.0, 3.0, 3.0),
        ("alice", "Alice", "I'm doing great!", "happy", 1.0, 6.0, 2.0),
    ]
    assert len(timeline.turns) == 3
    for turn, values in zip(timeline.turns, expected, strict=True):
        assert (
            turn.character_id, turn.character_name, turn.dialogue, turn.emotion,
            turn.emotion_strength, turn.start_time, turn.duration,
        ) == values
    assert calculate_total_duration(timeline) == 8.0
    validate_timeline(timeline)

    expect_value_error("empty dialogue", lambda: create_turn("alice", "Alice", "", "happy", 1.0, 3))
    expect_value_error("unsupported emotion", lambda: create_turn("alice", "Alice", "Hello", "excited", 1.0, 3))
    expect_value_error("negative duration", lambda: create_turn("alice", "Alice", "Hello", "happy", 1.0, -1))
    expect_value_error("invalid emotion strength", lambda: create_turn("alice", "Alice", "Hello", "happy", 0, 3))
    expect_value_error(
        "overlapping start time",
        lambda: build_timeline([
            create_turn("alice", "Alice", "Hello", "happy", 1.0, 3, start_time=0),
            create_turn("bob", "Bob", "Hi", "neutral", 1.0, 2, start_time=2),
        ]),
    )

    print("Conversation timeline test passed.")
    for index, turn in enumerate(timeline.turns, start=1):
        print(f"Turn {index}: {turn.character_name} | start={turn.start_time:g}s | duration={turn.duration:g}s | {turn.emotion}")
    print(f"Total duration: {timeline.total_duration:g} seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
