# Final Conversation Composer

This FFmpeg-only module combines existing conversation turn videos into one
sequential, side-by-side two-character conversation. It does not import or call
FLOAT, create audio, or regenerate any turns.

`compose_conversation(timeline, turn_videos, output_path)` uses the first
timeline character on the left and the second on the right. The active
speaker's turn video occupies its exact scheduled duration; the other speaker
uses a cloned representative frame. Active audio is trimmed/padded to each
turn's duration and concatenated in timeline order, so audio is never mixed.

Run the standalone test:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\conversation_composer\test_composer.py
```
