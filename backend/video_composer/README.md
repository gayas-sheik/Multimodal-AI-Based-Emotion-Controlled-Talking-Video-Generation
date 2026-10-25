# Two-person scene compositor

`compose_two_person_scene()` is an independent FFmpeg-only utility. It accepts
two already-generated videos, normalizes both to `512x512` at `25 FPS`, places
them side-by-side into a `1024x512` MP4, and mixes their audio streams.

Run the standalone test from the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\video_composer\test_composer.py
```

It uses `backend/test_output/api_generated.mp4` and
`backend/test_output/test_output.mp4`, creating
`backend/test_output/two_person_scene.mp4`.
