# FLOAT AI Talking Video Generator — Frontend

This React/Vite UI calls the local FastAPI backend at `http://127.0.0.1:8000`.
The backend must be running before the UI can generate a video.

## Install

From `FloatWebApp/frontend`:

```powershell
npm.cmd install
```

## Run the backend

From the project root:

```powershell
& "C:\Users\gayas\Documents\Final Year Project\PP-II\SentiGaurdAi\FloatAI\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\python_embeded\python.exe" backend\app\run.py
```

## Run the frontend

In another terminal, from `FloatWebApp/frontend`:

```powershell
npm.cmd run dev
```

Open the URL Vite prints (normally `http://127.0.0.1:5173`). Select an image,
audio, emotion, and strength, then click **Generate video**.

## Two-person conversation

Choose **Two-person conversation** in the application to use the existing
`POST /generate-conversation` API. This technical UI supports exactly two
characters (Alice and Bob) and three sequential dialogue turns. Upload a
portrait for each character, then configure each turn's speaker, dialogue,
audio, emotion, strength, and duration. The returned MP4 is shown in the page
and can be downloaded.

With FastAPI and Vite running, verify the full browser → API → FLOAT →
conversation composer flow with:

```powershell
npm.cmd run test:conversation
```


## End-to-end development smoke test

With both servers running, this runs local Microsoft Edge headlessly against the
actual React UI using the supplied project test files. It confirms the UI
receives a playable MP4 Blob from FLOAT. `playwright-core` is installed as a
development dependency and uses the system Microsoft Edge installation:

```powershell
npm.cmd run test:browser
```
