
"""Serialized multipart endpoint for the existing direct FLOAT adapter."""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
import uuid
from pathlib import Path

import cv2
import soundfile as sf
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.app.security import verify_api_key
from backend.float_engine.float_adapter import get_engine


logger = logging.getLogger(__name__)

router = APIRouter(tags=["generation"])

SUPPORTED_EMOTIONS = {
    "none",
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise",
}

PROJECT_ROOT = Path(__file__).resolve().parents[3]
JOBS_ROOT = PROJECT_ROOT / "backend" / ".jobs"

MAX_UPLOAD_BYTES = 100 * 1024 * 1024

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}


def _generation_lock(request: Request) -> asyncio.Lock:
    lock = getattr(request.app.state, "float_generation_lock", None)

    if lock is None:
        lock = asyncio.Lock()
        request.app.state.float_generation_lock = lock

    return lock


async def _write_upload(upload: UploadFile, destination: Path) -> None:
    total = 0

    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)

                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Upload exceeds the 100 MB limit.",
                    )

                output.write(chunk)
    finally:
        await upload.close()


def _validate_image(path: Path) -> None:
    image = cv2.imread(str(path))

    if image is None or image.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsupported image file.",
        )


def _validate_audio(path: Path) -> None:
    try:
        metadata = sf.info(str(path))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsupported audio file.",
        ) from error

    if metadata.frames <= 0 or metadata.samplerate <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file contains no readable samples.",
        )


def _cleanup_job(job_dir: Path) -> None:
    shutil.rmtree(job_dir, ignore_errors=True)


@router.post(
    "/generate",
    response_class=FileResponse,
    summary="Generate a FLOAT talking-head MP4",
)
async def generate(
    request: Request,
    _: None = Depends(verify_api_key),
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    emotion: str = Form("none"),
    emotion_strength: float = Form(1.0, ge=1.0),
) -> FileResponse:
    """Run one serialized FLOAT generation and stream its MP4 response."""

    emotion = emotion.strip().lower()

    if emotion not in SUPPORTED_EMOTIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Unsupported emotion. Choose one of: "
                f"{', '.join(sorted(SUPPORTED_EMOTIONS))}."
            ),
        )

    image_suffix = Path(image.filename or "upload.jpg").suffix.lower()
    audio_suffix = Path(audio.filename or "upload.wav").suffix.lower()

    if image_suffix not in IMAGE_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be JPG, JPEG, PNG, or WEBP.",
        )

    if audio_suffix not in AUDIO_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio must be WAV, MP3, FLAC, M4A, or OGG.",
        )

    JOBS_ROOT.mkdir(parents=True, exist_ok=True)

    job_dir = Path(
        tempfile.mkdtemp(
            prefix=f"float-{uuid.uuid4().hex[:8]}-",
            dir=JOBS_ROOT,
        )
    )

    image_path = job_dir / f"reference{image_suffix}"
    audio_path = job_dir / f"audio{audio_suffix}"
    output_path = job_dir / "generated.mp4"

    try:
        await _write_upload(image, image_path)
        await _write_upload(audio, audio_path)

        _validate_image(image_path)
        _validate_audio(audio_path)

        # Serialize GPU-heavy inference and keep the event loop responsive.
        async with _generation_lock(request):
            try:
                await asyncio.to_thread(
                    get_engine().generate_talking_video,
                    image_path,
                    audio_path,
                    emotion,
                    emotion_strength,
                    output_path=output_path,
                )
            except (FileNotFoundError, ValueError) as error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(error),
                ) from error
            except Exception as error:
                logger.exception(
                    "FLOAT generation failed for job %s",
                    job_dir.name,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="FLOAT generation failed. Check the server log.",
                ) from error

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FLOAT did not create an MP4 output.",
            )

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="float-generated.mp4",
            background=BackgroundTask(_cleanup_job, job_dir),
        )

    except HTTPException:
        _cleanup_job(job_dir)
        raise

    except Exception as error:
        logger.exception(
            "Request processing failed for job %s",
            job_dir.name,
        )
        _cleanup_job(job_dir)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request processing failed. Check the server log.",
        ) from error
