"""Thin orchestration layer for the existing conversation modules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from backend.conversation import ConversationTimeline, validate_timeline
from backend.conversation_composer import compose_conversation
from backend.conversation_generation import TurnGenerationResult, generate_conversation_turns


@dataclass(frozen=True)
class ConversationPipelineResult:
    """Successful result of timeline generation and final conversation composition."""

    output_path: Path
    total_duration: float
    turn_results: tuple[TurnGenerationResult, ...]
    number_of_turns: int
    character_ids: tuple[str, ...]
    status: str = "success"


def _require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} was not found: {resolved}")
    return resolved


def generate_full_conversation(
    timeline: ConversationTimeline,
    character_images: Mapping[str, str | Path],
    turn_audio_paths: Sequence[str | Path],
    output_path: str | Path,
) -> ConversationPipelineResult:
    """Generate timeline turns through FLOAT, then compose one final MP4.

    This is intentionally an orchestrator only: it delegates sequential GPU
    work to ``generate_conversation_turns`` and FFmpeg composition to
    ``compose_conversation``. No FLOAT or filter-graph logic is duplicated.
    """
    validate_timeline(timeline)
    if len(turn_audio_paths) != len(timeline.turns):
        raise ValueError("turn_audio_paths must contain exactly one audio path for every timeline turn.")

    character_ids = tuple(dict.fromkeys(turn.character_id for turn in timeline.turns))
    missing_images = [character_id for character_id in character_ids if character_id not in character_images]
    if missing_images:
        raise ValueError(f"Missing reference image mapping for character IDs: {', '.join(missing_images)}.")
    resolved_images = {
        character_id: _require_file(character_images[character_id], f"Reference image for character {character_id!r}")
        for character_id in character_ids
    }
    resolved_audio = tuple(
        _require_file(audio_path, f"Audio for turn {index}")
        for index, audio_path in enumerate(turn_audio_paths, start=1)
    )
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    turns_directory = output_path.parent / "turns"

    try:
        turn_results = tuple(generate_conversation_turns(
            timeline=timeline,
            character_images=resolved_images,
            turn_audio_paths=resolved_audio,
            output_dir=turns_directory,
        ))
    except Exception as error:
        raise RuntimeError(f"Conversation turn generation failed: {error}") from error
    if len(turn_results) != len(timeline.turns):
        raise RuntimeError("Conversation turn generation did not return one result per timeline turn.")
    for result in turn_results:
        _require_file(result.video_path, f"Generated video for turn {result.turn_index}")

    try:
        final_path = compose_conversation(timeline, turn_results, output_path)
    except Exception as error:
        raise RuntimeError(f"Final conversation composition failed: {error}") from error
    _require_file(final_path, "Final conversation output")
    return ConversationPipelineResult(
        output_path=final_path,
        total_duration=timeline.total_duration,
        turn_results=turn_results,
        number_of_turns=len(turn_results),
        character_ids=character_ids,
    )
