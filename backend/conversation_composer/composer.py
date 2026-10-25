"""Compose a sequential timeline of existing FLOAT turn videos into one MP4."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from backend.conversation import ConversationTimeline, validate_timeline


TARGET_WIDTH = 512
TARGET_HEIGHT = 512
TARGET_FPS = 25


def _ffmpeg_path() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as error:
        raise RuntimeError("FFmpeg was not found on PATH and imageio_ffmpeg is unavailable.") from error


def _video_path(turn_video: object, index: int) -> Path:
    value = getattr(turn_video, "video_path", turn_video)
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Turn {index} video was not found: {path}")
    return path


def _format_time(value: float) -> str:
    return f"{value:.9f}".rstrip("0").rstrip(".")


def build_conversation_command(
    timeline: ConversationTimeline,
    turn_videos: Sequence[object],
    output_path: str | Path,
    *,
    layout: str = "side_by_side",
) -> list[str]:
    """Build one FFmpeg command for a contiguous two-character timeline.

    The first character appearing in the timeline occupies the left side; the
    second occupies the right. Each turn video is active only for that turn's
    scheduled duration. A cloned first frame of the other character remains on
    screen. Audio streams are trimmed/padded per turn and concatenated, never
    mixed, so only the active speaker is audible in each segment.
    """
    validate_timeline(timeline)
    if layout != "side_by_side":
        raise ValueError("Only layout='side_by_side' is supported.")
    if len(turn_videos) != len(timeline.turns):
        raise ValueError("turn_videos must contain exactly one video per timeline turn.")
    character_order: list[str] = []
    for turn in timeline.turns:
        if turn.character_id not in character_order:
            character_order.append(turn.character_id)
    if len(character_order) != 2:
        raise ValueError("This prototype requires exactly two distinct character IDs.")
    video_paths = [_video_path(video, index) for index, video in enumerate(turn_videos, start=1)]
    total_duration = _format_time(timeline.total_duration)
    seed_indices = {character_id: next(index for index, turn in enumerate(timeline.turns) if turn.character_id == character_id) for character_id in character_order}

    filters: list[str] = []
    active_labels: list[str] = []
    # Every filter output label can only have one consumer.  Prepare an
    # independent frozen-frame stream for each timeline segment that needs a
    # non-speaking character, rather than reusing one static label twice.
    static_use_counts = {
        character_id: sum(1 for turn in timeline.turns if turn.character_id != character_id)
        for character_id in character_order
    }
    static_labels: dict[str, list[str]] = {}
    normalize = (
        f"fps={TARGET_FPS},scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
    )
    for index, turn in enumerate(timeline.turns):
        active = f"active{index}"
        if seed_indices[turn.character_id] == index:
            seed = f"seed{index}"
            static_base = f"static_base_{turn.character_id}"
            static_outputs = [f"static_{turn.character_id}_{slot}" for slot in range(static_use_counts[turn.character_id])]
            filters.append(f"[{index}:v]{normalize},split=2[{active}][{seed}]")
            # The representative first frame is safely extended for use in
            # every other speaker's timeline segment.
            filters.append(
                f"[{seed}]trim=duration=0.04,setpts=PTS-STARTPTS,"
                f"tpad=stop_mode=clone:stop_duration={total_duration}[{static_base}]"
            )
            filters.append(f"[{static_base}]split={len(static_outputs)}{''.join(f'[{label}]' for label in static_outputs)}")
            static_labels[turn.character_id] = static_outputs
        else:
            filters.append(f"[{index}:v]{normalize}[{active}]")
        active_labels.append(active)

    video_segments: list[str] = []
    audio_segments: list[str] = []
    left_character, right_character = character_order
    for index, turn in enumerate(timeline.turns):
        duration = _format_time(turn.duration)
        active = f"turn_video{index}"
        audio = f"turn_audio{index}"
        # tpad/apad cover an unusually short source safely. The final trim
        # always makes this segment exactly the timeline turn duration.
        filters.append(
            f"[{active_labels[index]}]trim=duration={duration},setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={duration},trim=duration={duration}[{active}]"
        )
        filters.append(
            f"[{index}:a]atrim=duration={duration},asetpts=PTS-STARTPTS,"
            f"apad=pad_dur={duration},atrim=duration={duration}[{audio}]"
        )
        other_character = right_character if turn.character_id == left_character else left_character
        static_segment = f"static_segment{index}"
        static_source = static_labels[other_character].pop(0)
        filters.append(f"[{static_source}]trim=duration={duration},setpts=PTS-STARTPTS[{static_segment}]")
        segment = f"segment{index}"
        if turn.character_id == left_character:
            filters.append(f"[{active}][{static_segment}]hstack=inputs=2[{segment}]")
        else:
            filters.append(f"[{static_segment}][{active}]hstack=inputs=2[{segment}]")
        video_segments.append(f"[{segment}]")
        audio_segments.append(f"[{audio}]")

    filters.append(f"{''.join(video_segments)}concat=n={len(video_segments)}:v=1:a=0[video]")
    filters.append(f"{''.join(audio_segments)}concat=n={len(audio_segments)}:v=0:a=1[audio]")
    return [
        _ffmpeg_path(), "-y",
        *[item for video_path in video_paths for item in ("-i", str(video_path))],
        "-filter_complex", ";".join(filters),
        "-map", "[video]", "-map", "[audio]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(TARGET_FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(Path(output_path).expanduser().resolve()),
    ]


def compose_conversation(
    timeline: ConversationTimeline,
    turn_videos: Sequence[object],
    output_path: str | Path,
    *,
    layout: str = "side_by_side",
) -> Path:
    """Create the final sequential conversation MP4 using only existing videos."""
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_conversation_command(timeline, turn_videos, output_path, layout=layout)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversation composition failed:\n{result.stderr}")
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg did not create the final conversation MP4: {output_path}")
    return output_path
