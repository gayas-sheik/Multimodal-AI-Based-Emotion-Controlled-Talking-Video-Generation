"""Run timeline -> existing turn generation -> existing final composition."""

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
from backend.conversation_pipeline import generate_full_conversation


def main() -> int:
    test_data = PROJECT_ROOT / "backend" / "test_data"
    image_path = test_data / "download.jpg"
    audio_path = test_data / "03-01-02-02-02-01-01.wav"
    output_path = PROJECT_ROOT / "backend" / "test_output" / "conversation_pipeline" / "final_conversation.mp4"
    timeline = build_timeline([
        create_turn("alice", "Alice", "Hello Bob, how are you?", "happy", 1.0, 3),
        create_turn("bob", "Bob", "I'm fine, Alice. How are you?", "neutral", 1.0, 3),
        create_turn("alice", "Alice", "I'm doing great!", "happy", 1.0, 2),
    ])
    result = generate_full_conversation(
        timeline=timeline,
        character_images={"alice": image_path, "bob": image_path},
        turn_audio_paths=[audio_path, audio_path, audio_path],
        output_path=output_path,
    )
    assert result.status == "success"
    assert result.number_of_turns == 3
    assert result.character_ids == ("alice", "bob")
    assert [turn.character_id for turn in result.turn_results] == ["alice", "bob", "alice"]
    assert all(turn.video_path.is_file() for turn in result.turn_results)
    assert result.output_path.is_file() and result.output_path.stat().st_size > 0

    capture = cv2.VideoCapture(str(result.output_path))
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
    assert abs(duration - 8.0) <= 0.08
    audio_check = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(result.output_path), "-map", "0:a:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    assert audio_check.returncode == 0, audio_check.stderr
    print(f"Pipeline succeeded: {result.output_path}")
    print(f"Video: {width}x{height}, {fps:.2f} FPS, {duration:.2f} seconds, audio present")
    print("Turns: Alice -> Bob -> Alice; generated sequentially by the existing conversation_generation module")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
