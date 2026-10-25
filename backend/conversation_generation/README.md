# Conversation Generation

This module bridges a validated `ConversationTimeline` to the existing direct
FLOAT adapter. It is intentionally independent of FastAPI, React, FFmpeg scene
composition, text-to-speech, and final conversation assembly.

```python
generate_conversation_turns(
    timeline,
    character_images={"alice": "alice.jpg", "bob": "bob.jpg"},
    turn_audio_paths=["alice_01.wav", "bob_01.wav", "alice_02.wav"],
    output_dir="outputs/conversation",
)
```

The function validates the timeline and assets, reuses a single process-local
`FloatEngine`, and calls it in order once per turn. The result list contains
timeline metadata plus each generated MP4 path. Timeline duration remains
scheduling metadata because FLOAT's existing adapter does not take an explicit
target duration.

Run the real integration test from the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\conversation_generation\test_generation.py
```
