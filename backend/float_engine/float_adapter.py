"""Direct inference adapter for the existing ComfyUI-FLOAT source tree.

This module never writes to or changes the ComfyUI/FLOAT installation.  It
imports the existing `generate.py` as an isolated package and uses its public
`InferenceAgent.run_inference` method.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import threading
import types
from pathlib import Path
from typing import Optional

import torch

from .config import FloatConfig


_ENGINE: Optional["FloatEngine"] = None
_ENGINE_LOCK = threading.Lock()
_SOURCE_PACKAGE = "_direct_float_source"
_EMOTIONS = {"none", "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"}


def _load_existing_inference_agent(config: FloatConfig):
    """Import existing generate.py without executing the custom node __init__.py.

    FLOAT.py imports `comfy.utils.ProgressBar`; placing the existing ComfyUI
    root on sys.path preserves that dependency unchanged.  A synthetic parent
    package lets generate.py keep its original relative imports (`.models`,
    `.options`) while avoiding the hyphenated directory-name import problem.
    """
    # The portable embedded Python cannot create Numba cache entries beside
    # Librosa in site-packages.  Librosa is imported by the original
    # generate.py, so redirect only its runtime cache to this new project.
    numba_cache = Path(__file__).resolve().parents[1] / ".numba_cache"
    numba_cache.mkdir(exist_ok=True)
    os.environ.setdefault("NUMBA_CACHE_DIR", str(numba_cache))

    comfy_root_string = str(config.comfy_root)
    if comfy_root_string not in sys.path:
        sys.path.insert(0, comfy_root_string)

    if _SOURCE_PACKAGE not in sys.modules:
        source_package = types.ModuleType(_SOURCE_PACKAGE)
        source_package.__path__ = [str(config.float_root)]
        source_package.__package__ = _SOURCE_PACKAGE
        sys.modules[_SOURCE_PACKAGE] = source_package

    module = importlib.import_module(f"{_SOURCE_PACKAGE}.generate")
    return module.InferenceAgent, module.BaseOptionsJson


class FloatEngine:
    """A process-local, single-instance FLOAT inference engine."""

    def __init__(self, config: Optional[FloatConfig] = None) -> None:
        self.config = config or FloatConfig.from_environment()
        self.config.validate()
        self.agent = None

    def load(self) -> None:
        """Load the existing FLOAT checkpoint and its two local Wav2Vec models once."""
        if self.agent is not None:
            return
        if not torch.cuda.is_available():
            raise RuntimeError("FLOAT direct inference requires CUDA, but CUDA is unavailable.")

        inference_agent, options = _load_existing_inference_agent(self.config)
        # This is the same options setup used by LoadFloatModels.loadmodel().
        options.rank, options.ngpus = 0, 1
        options.ckpt_path = str(self.config.model_path)
        options.pretrained_dir = str(self.config.model_path.parent)
        options.wav2vec_model_path = str(self.config.wav2vec_model_path)
        options.audio2emotion_path = str(self.config.emotion_model_path)
        self.agent = inference_agent(options)

    def generate_talking_video(
        self,
        image_path: str | Path,
        audio_path: str | Path,
        emotion: str = "none",
        emotion_strength: float = 1.0,
        *,
        fps: float = 25,
        seed: int = 62064758300528,
        a_cfg_scale: float = 2.0,
        r_cfg_scale: float = 1.0,
        crop: bool = False,
        output_path: str | Path | None = None,
    ) -> Path:
        """Generate an MP4 from a reference image and speech audio.

        `emotion_strength` is passed directly as FLOAT's `e_cfg_scale`.
        `crop` retains the node's meaning: False skips face cropping.
        """
        image_path = Path(image_path).expanduser().resolve()
        audio_path = Path(audio_path).expanduser().resolve()
        if not image_path.is_file():
            raise FileNotFoundError(f"Reference image not found: {image_path}")
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        emotion = emotion.lower().strip()
        if emotion not in _EMOTIONS:
            raise ValueError(f"Unsupported emotion {emotion!r}; choose one of {sorted(_EMOTIONS)}.")
        if emotion_strength < 1.0 or a_cfg_scale < 1.0 or r_cfg_scale < 1.0:
            raise ValueError("FLOAT CFG scales must be at least 1.0.")
        if fps <= 0:
            raise ValueError("fps must be positive.")

        self.load()
        assert self.agent is not None
        if output_path is None:
            output_path = Path.cwd() / "test_output.mp4"
        output_path = Path(output_path).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # This is the exact public wrapper signature discovered in generate.py.
        self.agent.G.to(self.agent.rank)
        self.agent.opt.fps = fps
        try:
            with torch.inference_mode():
                frames = self.agent.run_inference(
                    None,
                    str(image_path),
                    str(audio_path),
                    a_cfg_scale=a_cfg_scale,
                    r_cfg_scale=r_cfg_scale,
                    e_cfg_scale=emotion_strength,
                    emo=None if emotion == "none" else emotion,
                    no_crop=not crop,
                    seed=seed,
                )
            self._encode_video(frames, audio_path, output_path, fps)
            return output_path
        finally:
            # Preserve the Comfy node's offload behaviour while keeping this
            # one engine instance reusable for subsequent requests.
            self.agent.G.to("cpu")
            if "frames" in locals():
                del frames
            torch.cuda.empty_cache()

    @staticmethod
    def _ffmpeg_path() -> str:
        executable = shutil.which("ffmpeg")
        if executable:
            return executable
        try:
            import imageio_ffmpeg

            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError as error:
            raise RuntimeError("FFmpeg was not found on PATH and imageio_ffmpeg is unavailable.") from error

    def _encode_video(self, frames: torch.Tensor, audio_path: Path, output_path: Path, fps: float) -> None:
        """Encode FLOAT's CPU [T,H,W,3] float frames and mux original audio."""
        if frames.ndim != 4 or frames.shape[-1] != 3:
            raise ValueError(f"Expected FLOAT frames shaped [T,H,W,3], received {tuple(frames.shape)}.")
        video = frames.detach().clamp(0, 1).mul(255).to(torch.uint8).contiguous().numpy()
        height, width = int(video.shape[1]), int(video.shape[2])
        command = [
            self._ffmpeg_path(), "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
            "-i", str(audio_path),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-shortest", "-movflags", "+faststart", str(output_path),
        ]
        result = subprocess.run(command, input=video.tobytes(), capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("FFmpeg failed:\n" + result.stderr.decode(errors="replace"))
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError(f"FFmpeg completed but did not create a valid output: {output_path}")


def get_engine(config: Optional[FloatConfig] = None) -> FloatEngine:
    """Return the one lazily loaded engine for this Python process."""
    global _ENGINE
    with _ENGINE_LOCK:
        if _ENGINE is None:
            _ENGINE = FloatEngine(config)
        return _ENGINE


def generate_talking_video(
    image_path: str | Path,
    audio_path: str | Path,
    emotion: str,
    emotion_strength: float,
    fps: float = 25,
    seed: int = 62064758300528,
) -> Path:
    """Convenience API matching the initial standalone FLOAT use case."""
    return get_engine().generate_talking_video(
        image_path, audio_path, emotion, emotion_strength, fps=fps, seed=seed
    )
