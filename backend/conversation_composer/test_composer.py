"""Compose the existing generated FLOAT turns into one timeline-driven MP4."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import cv2
import imageio_ffmpeg


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.conversation import build_timeline, create_turn
from backend.conversation_composer import build_conversation_command, compose_conversation


def main() -> int:
    source_dir = PROJECT_ROOT / "backend" / "test_output" / "conversation_generation"
    turn_videos = [
        source_dir / "turn_001_alice.mp4",
        source_dir / "turn_002_bob.mp4",
        source_dir / "turn_003_alice.mp4",
    ]
    output_path = PROJECT_ROOT / "backend" / "test_output" / "conversation_composer" / "final_conversation.mp4"
    timeline = build_timeline([
        create_turn("alice", "Alice", "Hello Bob, how are you?", "happy", 1.0, 3),
        create_turn("bob", "Bob", "I'm fine, Alice. How are you?", "neutral", 1.0, 3),
        create_turn("alice", "Alice", "I'm doing great!", "happy", 1.0, 2),
    ])
    print("FFmpeg command:")
    print(subprocess.list2cmdline(build_conversation_command(timeline, turn_videos, output_path)))
    compose_conversation(timeline, turn_videos, output_path)

    capture = cv2.VideoCapture(str(output_path))
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    readable, _ = capture.read()
    capture.release()
    duration = frames / fps
    assert readable and frames > 0
    assert (width, height) == (1024, 512)
    assert fps == 25.0
    assert abs(duration - timeline.total_duration) <= 0.08
    audio_check = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output_path), "-map", "0:a:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    full_decode = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(output_path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    assert audio_check.returncode == 0, audio_check.stderr
    assert full_decode.returncode == 0, full_decode.stderr
    print(f"Conversation composition succeeded: {output_path}")
    print(f"Video: {width}x{height}, {fps:.2f} FPS, {duration:.2f} seconds, {frames} frames")
    print("Audio: active-turn sequence Alice -> Bob -> Alice; present and decodable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
