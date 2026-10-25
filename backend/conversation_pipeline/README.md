# Conversation Pipeline

`generate_full_conversation()` is a backend-only orchestration layer:

```text
ConversationTimeline
  -> generate_conversation_turns()  # existing sequential FLOAT bridge
  -> compose_conversation()         # existing FFmpeg final composer
  -> final MP4
```

It accepts a validated timeline, a mapping of character IDs to reference-image
paths, one prerecorded audio path per turn, and a final output path. It returns
`ConversationPipelineResult` with the final path, scheduling duration, turn
results, character IDs, and status.

The pipeline does not reimplement FLOAT or FFmpeg. Sequential GPU behavior is
provided by the existing `conversation_generation` module.

Example:

```python
result = generate_full_conversation(
    timeline,
    character_images={"alice": "alice.jpg", "bob": "bob.jpg"},
    turn_audio_paths=["alice_01.wav", "bob_01.wav", "alice_02.wav"],
    output_path="outputs/final_conversation.mp4",
)
```

Run the integration test from the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\conversation_pipeline\test_pipeline.py
```
