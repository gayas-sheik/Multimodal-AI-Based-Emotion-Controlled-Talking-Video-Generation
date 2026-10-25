# Direct FLOAT API (development)

The original ComfyUI/FLOAT installation is read-only. Web dependencies live in
`backend/vendor`, so they do not alter its embedded Python packages.

Start the API from the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\app\run.py
```

Test health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Test generation:

```powershell
curl.exe -X POST http://127.0.0.1:8000/generate -F "image=@backend/test_data/download.jpg" -F "audio=@backend/test_data/03-01-02-02-02-01-01.wav" -F "emotion=happy" -F "emotion_strength=1.0" -o generated-api.mp4
```

## Conversation generation

`POST /generate-conversation` is the two-character, three-turn technical API.
It accepts multipart fields `image_alice`, `image_bob`, `audio_turn_1`,
`audio_turn_2`, `audio_turn_3`, the names `alice_name` and `bob_name`, and
five fields per turn: `character`, `dialogue`, `emotion`, `emotion_strength`,
and `duration` (for example, `turn_1_character`). Character IDs must be
`alice` or `bob`; supported emotions are the existing FLOAT emotions.

The route creates a timeline through `backend.conversation`, then calls the
existing `generate_full_conversation()` pipeline. It returns the actual final
MP4 (`video/mp4`), not a filesystem path. Requests share the existing GPU lock
with `/generate`, so FLOAT generation is serialized. Validation errors return
4xx responses; internal pipeline errors return a generic 500 response and are
logged server-side.

Run the in-process FastAPI end-to-end test:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\app\routes\test_conversation_api.py
```
