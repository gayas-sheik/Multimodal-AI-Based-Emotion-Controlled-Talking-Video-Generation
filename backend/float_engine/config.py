"""Configuration for the existing, externally managed FLOAT installation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_DEFAULT_PORTABLE_ROOT = Path(
    r"C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI"
    r"\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable"
)


@dataclass(frozen=True)
class FloatConfig:
    """Resolved paths for the existing FLOAT and ComfyUI installation."""

    comfy_portable_root: Path
    comfy_root: Path
    float_root: Path
    model_path: Path
    wav2vec_model_path: Path
    emotion_model_path: Path

    @classmethod
    def from_environment(cls) -> "FloatConfig":
        """Create config from environment variables, retaining local defaults.

        FLOAT_ROOT is the existing ComfyUI-FLOAT custom-node directory.
        FLOAT_MODEL_PATH is the existing float.pth checkpoint.  Setting either
        is optional; the remaining paths are derived from COMFY_PORTABLE_ROOT.
        """
        portable_root = Path(
            os.environ.get("COMFY_PORTABLE_ROOT", str(_DEFAULT_PORTABLE_ROOT))
        ).expanduser().resolve()
        comfy_root = Path(os.environ.get("COMFY_ROOT", str(portable_root / "ComfyUI"))).expanduser().resolve()
        float_root = Path(
            os.environ.get(
                "FLOAT_ROOT", str(comfy_root / "custom_nodes" / "ComfyUI-FLOAT")
            )
        ).expanduser().resolve()
        models_root = Path(
            os.environ.get("FLOAT_MODELS_ROOT", str(comfy_root / "models" / "float"))
        ).expanduser().resolve()

        return cls(
            comfy_portable_root=portable_root,
            comfy_root=comfy_root,
            float_root=float_root,
            model_path=Path(
                os.environ.get("FLOAT_MODEL_PATH", str(models_root / "float.pth"))
            ).expanduser().resolve(),
            wav2vec_model_path=Path(
                os.environ.get(
                    "FLOAT_WAV2VEC_MODEL_PATH", str(models_root / "wav2vec2-base-960h")
                )
            ).expanduser().resolve(),
            emotion_model_path=Path(
                os.environ.get(
                    "FLOAT_EMOTION_MODEL_PATH",
                    str(models_root / "wav2vec-english-speech-emotion-recognition"),
                )
            ).expanduser().resolve(),
        )

    def validate(self) -> None:
        required_files = {
            "ComfyUI directory": self.comfy_root,
            "FLOAT source directory": self.float_root,
            "FLOAT checkpoint": self.model_path,
            "Wav2Vec2 model directory": self.wav2vec_model_path,
            "emotion model directory": self.emotion_model_path,
        }
        missing = [f"{name}: {path}" for name, path in required_files.items() if not path.exists()]
        if missing:
            raise FileNotFoundError("Missing required FLOAT installation paths:\n" + "\n".join(missing))
