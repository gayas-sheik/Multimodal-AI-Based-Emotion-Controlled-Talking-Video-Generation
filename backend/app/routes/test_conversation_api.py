"""End-to-end HTTP test for ``POST /generate-conversation``.

The test starts the FastAPI application in-process and sends a real multipart
HTTP request through FastAPI's test client.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VENDOR_DIR = PROJECT_ROOT / "backend" / "vendor"
for path in (PROJECT_ROOT, VENDOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import cv2
import imageio_ffmpeg
from fastapi.testclient import TestClient

from backend.app.main import create_app


TEST_DATA = PROJECT_ROOT / "backend" / "test_data"
OUTPUT_PATH = PROJECT_ROOT / "backend" / "test_output" / "api_conversation" / "final_conversation.mp4"


def _has_audio_stream(video_path: Path) -> bool:
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(video_path), "-map", "0:a:0", "-f", "null", "-"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return completed.returncode == 0


def main() -> None:
    image_path = TEST_DATA / "download.jpg"
    audio_path = TEST_DATA / "03-01-02-02-02-01-01.wav"
    for required in (image_path, audio_path):
        if not required.is_file():
            raise FileNotFoundError(f"Required API test file is missing: {required}")

    fields = {
        "alice_name": "Alice", "bob_name": "Bob",
        "turn_1_character": "alice", "turn_1_dialogue": "Hello Bob, how are you?", "turn_1_emotion": "happy", "turn_1_emotion_strength": "1.0", "turn_1_duration": "3",
        "turn_2_character": "bob", "turn_2_dialogue": "I'm fine, Alice. How are you?", "turn_2_emotion": "neutral", "turn_2_emotion_strength": "1.0", "turn_2_duration": "3",
        "turn_3_character": "alice", "turn_3_dialogue": "I'm doing great!", "turn_3_emotion": "happy", "turn_3_emotion_strength": "1.0", "turn_3_duration": "2",
    }
    with (
        image_path.open("rb") as alice_image,
        image_path.open("rb") as bob_image,
        audio_path.open("rb") as turn_1_audio,
        audio_path.open("rb") as turn_2_audio,
        audio_path.open("rb") as turn_3_audio,
        TestClient(create_app()) as client,
    ):
        response = client.post(
            "/generate-conversation",
            data=fields,
            files={
                "image_alice": ("download.jpg", alice_image, "image/jpeg"),
                "image_bob": ("download.jpg", bob_image, "image/jpeg"),
                "audio_turn_1": ("turn_1.wav", turn_1_audio, "audio/wav"),
                "audio_turn_2": ("turn_2.wav", turn_2_audio, "audio/wav"),
                "audio_turn_3": ("turn_3.wav", turn_3_audio, "audio/wav"),
            },
        )
    content_type = response.headers.get("content-type", "").split(";", 1)[0]
    payload = response.content
    if response.status_code != 200:
        raise AssertionError(f"Expected HTTP 200, got {response.status_code}: {response.text}")
    if content_type != "video/mp4":
        raise AssertionError(f"Expected video/mp4, got {content_type!r}.")
    if not payload:
        raise AssertionError("Conversation endpoint returned no video bytes.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(payload)
    capture = cv2.VideoCapture(str(OUTPUT_PATH))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    decoded, _ = capture.read()
    capture.release()
    duration = frames / fps if fps else 0
    if not decoded or (width, height) != (1024, 512) or abs(fps - 25) > 0.01 or abs(duration - 8) > 0.08:
        raise AssertionError(f"Unexpected video metadata: {width}x{height}, {fps:.2f} FPS, {frames} frames, {duration:.2f}s.")
    if not _has_audio_stream(OUTPUT_PATH):
        raise AssertionError("Returned MP4 has no decodable audio stream.")
    print(json.dumps({
        "status": "passed", "output": str(OUTPUT_PATH), "bytes": len(payload),
        "resolution": f"{width}x{height}", "fps": fps, "frames": frames, "duration": duration,
        "audio": "present and decodable",
    }))


if __name__ == "__main__":
    main()
