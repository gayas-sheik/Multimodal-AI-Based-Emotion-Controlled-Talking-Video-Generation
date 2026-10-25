"""Sequential bridge from conversation timeline turns to the existing FLOAT adapter."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from backend.conversation import ConversationTimeline, validate_timeline
from backend.float_engine.float_adapter import FloatEngine, get_engine


@dataclass(frozen=True)
class TurnGenerationResult:
    """Timeline metadata and generated MP4 for one completed FLOAT turn."""

    turn_index: int
    character_id: str
    character_name: str
    start_time: float
    duration: float
    emotion: str
    emotion_strength: float
    video_path: Path


def _safe_file_stem(character_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", character_id).strip("_") or "character"


def _require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} was not found: {resolved}")
    return resolved


def generate_conversation_turns(
    timeline: ConversationTimeline,
    character_images: Mapping[str, str | Path],
    turn_audio_paths: Sequence[str | Path],
    output_dir: str | Path,
    *,
    engine: FloatEngine | None = None,
    fps: float = 25,
    seed: int = 62064758300528,
) -> list[TurnGenerationResult]:
    """Generate one MP4 per conversation turn in timeline order.

    ``character_images`` maps each ``character_id`` to one reference image.
    ``turn_audio_paths`` supplies one prerecorded audio file per turn, in the
    same order as ``timeline.turns``. FLOAT has no explicit duration argument;
    ``DialogueTurn.duration`` is retained as timeline scheduling metadata.

    Calls are intentionally synchronous and sequential. A single engine is
    resolved once and reused, so its FLOAT checkpoint is not reloaded per turn.
    """
    validate_timeline(timeline)
    if len(turn_audio_paths) != len(timeline.turns):
        raise ValueError("turn_audio_paths must contain exactly one audio path for each timeline turn.")
    if fps <= 0:
        raise ValueError("fps must be positive.")

    resolved_images = {
        character_id: _require_file(image_path, f"Reference image for character {character_id!r}")
        for character_id, image_path in character_images.items()
    }
    resolved_audio = [_require_file(audio_path, f"Audio for turn {index}") for index, audio_path in enumerate(turn_audio_paths, start=1)]
    missing_characters = sorted({turn.character_id for turn in timeline.turns} - set(resolved_images))
    if missing_characters:
        raise ValueError(f"Missing reference image mapping for character IDs: {', '.join(missing_characters)}.")

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    float_engine = engine or get_engine()
    results: list[TurnGenerationResult] = []

    for turn_index, (turn, audio_path) in enumerate(zip(timeline.turns, resolved_audio, strict=True), start=1):
        output_path = output_dir / f"turn_{turn_index:03d}_{_safe_file_stem(turn.character_id)}.mp4"
        # This is deliberately a normal, ordered call: no threads, tasks, or
        # parallel workers are created around the GPU-bound FLOAT adapter.
        video_path = float_engine.generate_talking_video(
            image_path=resolved_images[turn.character_id],
            audio_path=audio_path,
            emotion=turn.emotion,
            emotion_strength=turn.emotion_strength,
            fps=fps,
            seed=seed,
            output_path=output_path,
        )
        results.append(TurnGenerationResult(
            turn_index=turn_index,
            character_id=turn.character_id,
            character_name=turn.character_name,
            start_time=float(turn.start_time),
            duration=turn.duration,
            emotion=turn.emotion,
            emotion_strength=turn.emotion_strength,
            video_path=video_path,
        ))
    return results
