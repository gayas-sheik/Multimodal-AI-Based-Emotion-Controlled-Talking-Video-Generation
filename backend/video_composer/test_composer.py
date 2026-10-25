"""Standalone integration test for the independent two-person compositor."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.video_composer.composer import _ffmpeg_path, build_two_person_command, compose_two_person_scene


def main() -> int:
    output_dir = PROJECT_ROOT / "backend" / "test_output"
    person1 = output_dir / "api_generated.mp4"
    person2 = output_dir / "test_output.mp4"
    output = output_dir / "two_person_scene.mp4"
    command = build_two_person_command(person1, person2, output)
    print("FFmpeg command:")
    print(subprocess.list2cmdline(command))
    compose_two_person_scene(person1, person2, output)

    capture = cv2.VideoCapture(str(output))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ok, first_frame = capture.read()
    capture.release()
    if not ok or first_frame is None or frame_count <= 0:
        raise RuntimeError("Composed MP4 has no decodable video frames.")

    # Decode the optional audio stream explicitly; this proves it was muxed.
    audio_check = subprocess.run(
        [_ffmpeg_path(), "-v", "error", "-i", str(output), "-map", "0:a:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    if audio_check.returncode != 0:
        raise RuntimeError(f"Composed MP4 audio stream is not decodable:\n{audio_check.stderr}")

    print(f"Composition succeeded: {output}")
    print(f"Video: {width}x{height}, {fps:.2f} FPS, {frame_count / fps:.2f} seconds, {frame_count} frames")
    print("Audio: present and decodable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
