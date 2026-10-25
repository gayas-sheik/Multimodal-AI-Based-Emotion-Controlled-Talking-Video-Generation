
"""API adapter for the existing full conversation generation pipeline."""

from __future__ import annotations

import asyncio
import logging
import tempfile
import uuid
from pathlib import Path

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
from backend.conversation import build_timeline, create_turn, validate_timeline
from backend.conversation_pipeline import generate_full_conversation

from .generate import (
    AUDIO_SUFFIXES,
    IMAGE_SUFFIXES,
    JOBS_ROOT,
    _cleanup_job,
    _generation_lock,
    _validate_audio,
    _validate_image,
    _write_upload,
)


router = APIRouter(tags=["conversation"])
logger = logging.getLogger(__name__)

CHARACTER_IDS = frozenset({"alice", "bob"})


def _upload_suffix(
    upload: UploadFile,
    default_name: str,
    allowed_suffixes: set[str],
    label: str,
) -> str:
    suffix = Path(upload.filename or default_name).suffix.lower()

    if suffix not in allowed_suffixes:
        allowed = ", ".join(sorted(allowed_suffixes))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label} has an unsupported file type. Allowed: {allowed}.",
        )

    return suffix


def _validate_character_id(character_id: str, turn_index: int) -> str:
    normalized = character_id.strip().lower()

    if normalized not in CHARACTER_IDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Turn {turn_index} character must be either 'alice' or 'bob'.",
        )

    return normalized


def _build_request_timeline(
    *,
    alice_name: str,
    bob_name: str,
    character_ids: tuple[str, str, str],
    dialogues: tuple[str, str, str],
    emotions: tuple[str, str, str],
    emotion_strengths: tuple[float, float, float],
    durations: tuple[float, float, float],
):
    names = {"alice": alice_name, "bob": bob_name}

    try:
        turns = [
            create_turn(
                character_id=character_id,
                character_name=names[character_id],
                dialogue=dialogue,
                emotion=emotion,
                emotion_strength=emotion_strength,
                duration=duration,
            )
            for character_id, dialogue, emotion, emotion_strength, duration in zip(
                character_ids,
                dialogues,
                emotions,
                emotion_strengths,
                durations,
                strict=True,
            )
        ]

        timeline = build_timeline(turns)
        validate_timeline(timeline)

        return timeline

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.post(
    "/generate-conversation",
    response_class=FileResponse,
    summary="Generate a two-character, three-turn FLOAT conversation MP4",
)
async def generate_conversation(
    request: Request,
    _: None = Depends(verify_api_key),
    image_alice: UploadFile = File(...),
    image_bob: UploadFile = File(...),
    audio_turn_1: UploadFile = File(...),
    audio_turn_2: UploadFile = File(...),
    audio_turn_3: UploadFile = File(...),
    alice_name: str = Form(...),
    bob_name: str = Form(...),
    turn_1_character: str = Form(...),
    turn_1_dialogue: str = Form(...),
    turn_1_emotion: str = Form(...),
    turn_1_emotion_strength: float = Form(...),
    turn_1_duration: float = Form(...),
    turn_2_character: str = Form(...),
    turn_2_dialogue: str = Form(...),
    turn_2_emotion: str = Form(...),
    turn_2_emotion_strength: float = Form(...),
    turn_2_duration: float = Form(...),
    turn_3_character: str = Form(...),
    turn_3_dialogue: str = Form(...),
    turn_3_emotion: str = Form(...),
    turn_3_emotion_strength: float = Form(...),
    turn_3_duration: float = Form(...),
) -> FileResponse:
    """Save job assets and delegate to the full conversation pipeline."""

    character_ids = (
        _validate_character_id(turn_1_character, 1),
        _validate_character_id(turn_2_character, 2),
        _validate_character_id(turn_3_character, 3),
    )

    image_suffixes = (
        _upload_suffix(image_alice, "alice.jpg", IMAGE_SUFFIXES, "Alice image"),
        _upload_suffix(image_bob, "bob.jpg", IMAGE_SUFFIXES, "Bob image"),
    )

    audio_uploads = (audio_turn_1, audio_turn_2, audio_turn_3)

    audio_suffixes = tuple(
        _upload_suffix(
            upload,
            f"turn-{index}.wav",
            AUDIO_SUFFIXES,
            f"Audio for turn {index}",
        )
        for index, upload in enumerate(audio_uploads, start=1)
    )

    timeline = _build_request_timeline(
        alice_name=alice_name,
        bob_name=bob_name,
        character_ids=character_ids,
        dialogues=(turn_1_dialogue, turn_2_dialogue, turn_3_dialogue),
        emotions=(turn_1_emotion, turn_2_emotion, turn_3_emotion),
        emotion_strengths=(
            turn_1_emotion_strength,
            turn_2_emotion_strength,
            turn_3_emotion_strength,
        ),
        durations=(turn_1_duration, turn_2_duration, turn_3_duration),
    )

    JOBS_ROOT.mkdir(parents=True, exist_ok=True)

    job_dir = Path(
        tempfile.mkdtemp(
            prefix=f"conversation-{uuid.uuid4().hex[:8]}-",
            dir=JOBS_ROOT,
        )
    )

    alice_path = job_dir / f"alice{image_suffixes[0]}"
    bob_path = job_dir / f"bob{image_suffixes[1]}"

    audio_paths = tuple(
        job_dir / f"turn_{index}{suffix}"
        for index, suffix in enumerate(audio_suffixes, start=1)
    )

    try:
        await _write_upload(image_alice, alice_path)
        await _write_upload(image_bob, bob_path)

        for upload, destination in zip(audio_uploads, audio_paths, strict=True):
            await _write_upload(upload, destination)

        _validate_image(alice_path)
        _validate_image(bob_path)

        for audio_path in audio_paths:
            _validate_audio(audio_path)

        async with _generation_lock(request):
            try:
                result = await asyncio.to_thread(
                    generate_full_conversation,
                    timeline,
                    {"alice": alice_path, "bob": bob_path},
                    audio_paths,
                    job_dir / "final_conversation.mp4",
                )

            except (FileNotFoundError, ValueError) as error:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(error),
                ) from error

            except Exception as error:
                logger.exception(
                    "Conversation pipeline failed for job %s",
                    job_dir.name,
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Conversation generation failed. Check the server log.",
                ) from error

        if not result.output_path.is_file() or result.output_path.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Conversation pipeline did not create an MP4 output.",
            )

        return FileResponse(
            result.output_path,
            media_type="video/mp4",
            filename="float-conversation.mp4",
            background=BackgroundTask(_cleanup_job, job_dir),
        )

    except HTTPException:
        _cleanup_job(job_dir)
        raise

    except Exception as error:
        logger.exception(
            "Conversation request processing failed for job %s",
            job_dir.name,
        )

        _cleanup_job(job_dir)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation request processing failed.",
        ) from error
