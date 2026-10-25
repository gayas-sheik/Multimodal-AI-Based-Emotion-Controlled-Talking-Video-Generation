"""Run the direct FLOAT integration test with the existing embedded Python."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.float_engine.float_adapter import get_engine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run direct FLOAT inference on one image and WAV file.")
    parser.add_argument("--image", type=Path, default=PROJECT_ROOT / "backend" / "test_data" / "reference.jpg")
    parser.add_argument("--audio", type=Path, default=PROJECT_ROOT / "backend" / "test_data" / "audio.wav")
    args = parser.parse_args()
    image_path = args.image.expanduser().resolve()
    audio_path = args.audio.expanduser().resolve()
    output_path = PROJECT_ROOT / "backend" / "test_output" / "test_output.mp4"

    missing = [path for path in (image_path, audio_path) if not path.is_file()]
    if missing:
        print("Test input files are required before FLOAT can run:")
        for path in missing:
            print(f"  - {path}")
        print("Place a single-face reference JPG and a speech WAV at those exact paths, then rerun this test.")
        return 2

    output = get_engine().generate_talking_video(
        image_path=image_path,
        audio_path=audio_path,
        emotion="happy",
        emotion_strength=1.0,
        fps=25,
        seed=62064758300528,
        output_path=output_path,
    )
    print(f"FLOAT direct inference succeeded: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
