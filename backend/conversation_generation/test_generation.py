"""Run a real sequential ConversationTimeline -> FLOAT integration test."""

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
from backend.conversation_generation import generate_conversation_turns


def verify_mp4(path: Path) -> tuple[int, int, float, float]:
    capture = cv2.VideoCapture(str(path))
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    readable, _ = capture.read()
    capture.release()
    if not readable or frames <= 0:
        raise AssertionError(f"{path.name} contains no decodable video frames.")
    audio = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(path), "-map", "0:a:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    if audio.returncode != 0:
        raise AssertionError(f"{path.name} contains no decodable audio stream:\n{audio.stderr}")
    return width, height, fps, frames / fps


def main() -> int:
    test_data = PROJECT_ROOT / "backend" / "test_data"
    image_path = test_data / "download.jpg"
    audio_path = test_data / "03-01-02-02-02-01-01.wav"
    output_dir = PROJECT_ROOT / "backend" / "test_output" / "conversation_generation"
    timeline = build_timeline([
        create_turn("alice", "Alice", "Hello Bob, how are you?", "happy", 1.0, 3),
        create_turn("bob", "Bob", "I'm fine, Alice. How are you?", "neutral", 1.0, 3),
        create_turn("alice", "Alice", "I'm doing great!", "happy", 1.0, 2),
    ])
    assert len(timeline.turns) == 3
    assert [turn.start_time for turn in timeline.turns] == [0.0, 3.0, 6.0]
    assert timeline.total_duration == 8.0

    results = generate_conversation_turns(
        timeline=timeline,
        character_images={"alice": image_path, "bob": image_path},
        turn_audio_paths=[audio_path, audio_path, audio_path],
        output_dir=output_dir,
    )
    assert len(results) == 3
    assert [result.character_id for result in results] == ["alice", "bob", "alice"]
    assert [result.start_time for result in results] == [0.0, 3.0, 6.0]
    assert [result.duration for result in results] == [3.0, 3.0, 2.0]
    assert [result.emotion for result in results] == ["happy", "neutral", "happy"]
    assert [result.emotion_strength for result in results] == [1.0, 1.0, 1.0]

    print("Conversation generations completed sequentially:")
    for result in results:
        assert result.video_path.is_file() and result.video_path.stat().st_size > 0
        width, height, fps, duration = verify_mp4(result.video_path)
        print(
            f"  Turn {result.turn_index}: {result.video_path.name} | "
            f"{width}x{height}, {fps:.2f} FPS, {duration:.2f}s, audio present | "
            f"{result.character_id}, {result.emotion}, strength={result.emotion_strength:g}"
        )
    print(f"Timeline schedule remains {timeline.total_duration:g} seconds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
