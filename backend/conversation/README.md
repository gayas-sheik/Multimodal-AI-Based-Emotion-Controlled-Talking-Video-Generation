# Conversation Timeline Engine

This standalone module models one sequential conversation. It has no FastAPI,
React, FLOAT, FFmpeg, audio, or video dependency.

Each `DialogueTurn` stores:

- `character_id`, `character_name`, and `dialogue`
- FLOAT-compatible `emotion` and `emotion_strength`
- `start_time` and `duration`

Use `create_turn()` to validate individual turns, then `build_timeline()` to
fill omitted start times and produce a contiguous `ConversationTimeline`.

Run the test from the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\conversation\test_timeline.py
```
