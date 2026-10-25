
# SentioGuard AI
## Multimodal AI-Based Emotion-Controlled Talking Video Generation

**Live website:** https://sentioguard-ai-web.pages.dev/

SentioGuard AI is a web application for generating emotion-controlled talking-head videos. It combines a reference portrait, speech audio, and a selected emotion to generate a video using the existing FLOAT/ComfyUI pipeline.

## Features

- **Talking-head generation:** Generate a video from a reference image and speech audio.
- **Emotion control:** Select a supported emotion and adjust its strength.
- **Conversation generation:** Create a two-character conversation with Alice and Bob across three sequential dialogue turns.
- **Video output:** View and download the generated MP4.
- **Web interface:** React-based frontend connected to a FastAPI backend.

## Architecture

```text
User
 |
 v
React + Vite Frontend
 |
 v
Cloudflare Worker Gateway
 |
 v
FastAPI Backend
 |
 v
FLOAT / ComfyUI Pipeline
 |
 v
Generated MP4
```

The deployed website uses Cloudflare Pages. The Worker gateway forwards API requests to the backend and is configured separately in Cloudflare. Video generation requires the backend machine and its FLOAT/ComfyUI environment to be running and reachable.

The Cloudflare Worker source is not included in this repository.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend API | Python, FastAPI, Uvicorn |
| Video generation | FLOAT with ComfyUI |
| Frontend deployment | Cloudflare Pages |
| API gateway | Cloudflare Workers |
| Backend connectivity | Cloudflare Tunnel, when available |
| Browser testing | Playwright Core with Microsoft Edge |

## Project Structure

```text
FloatWebApp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── run.py
│   │   └── routes/
│   ├── conversation/
│   ├── test_data/
│   ├── vendor/
│   └── requirements-api.txt
├── frontend/
│   ├── src/
│   ├── scripts/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

This is a simplified overview; consult the repository for the complete structure.

## Requirements

- Windows is used by the current development setup.
- Node.js and npm.
- An existing portable ComfyUI installation containing the FLOAT workflow and required models.
- The Python environment supplied with that installation.
- Cloudflare Tunnel and a configured Worker if using the deployed frontend with a locally hosted backend.

FLOAT model files and the portable ComfyUI installation are external dependencies and are not included in this repository.

## Configuration

Copy `.env.example` to `.env` in the project root and configure the path to your existing portable ComfyUI installation.

Example:

```dotenv
COMFY_PORTABLE_ROOT=C:\path\to\ComfyUI_windows_portable
```

The example file documents optional FLOAT model-path overrides. Set them only when needed.

Keep `.env` private. Never commit API keys, tunnel tokens, credentials, or other secrets.

## Running the Backend

Open PowerShell in the project root.

Set the path to your existing portable ComfyUI installation:

```powershell
$env:COMFY_PORTABLE_ROOT = "C:\path\to\ComfyUI_windows_portable"
```

Start the API using that installation's embedded Python:

```powershell
$portable = $env:COMFY_PORTABLE_ROOT
& "$portable\python_embeded\python.exe" ".\backend\app\run.py"
```

The API listens on `http://127.0.0.1:8000`.

Check its health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "float-direct-inference"
}
```

The backend API dependencies are listed in `backend/requirements-api.txt`. The current setup uses `backend/vendor` for its web dependencies rather than installing them into the external ComfyUI environment.

## Running the Frontend

Open a second terminal:

```powershell
Set-Location .\frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173`.

To create a production build:

```powershell
npm.cmd run build
```

The generated `frontend/dist/` directory is build output and should not be committed.

## API Endpoints

### Health check

`GET /health`

Returns the API's health status. This endpoint does not verify that the FLOAT pipeline can successfully generate a video.

### Single talking-head video

`POST /generate`

Multipart form fields:

| Field | Description |
|---|---|
| `image` | Reference portrait |
| `audio` | Speech audio file |
| `emotion` | Supported emotion |
| `emotion_strength` | Emotion strength |

The endpoint returns an MP4 video when generation succeeds.

### Two-person conversation

`POST /generate-conversation`

The conversation endpoint accepts portraits for Alice and Bob, three audio files, character names, and configuration for each dialogue turn.

The supported interface is designed for two characters and three sequential turns. Each turn specifies its speaker, dialogue, emotion, emotion strength, and duration.

The endpoint returns the composed MP4 when generation succeeds.

Refer to the backend route implementations for the current validation rules and supported values.

## Testing

Run these commands from `frontend/`.

Build the frontend:

```powershell
npm.cmd run build
```

Test the conversation API flow:

```powershell
npm.cmd run test:conversation
```

Run the browser smoke test:

```powershell
npm.cmd run test:browser
```

The conversation and browser tests require the corresponding backend and browser-test prerequisites described in `frontend/README.md`.

## Deployment Notes

- The frontend is hosted on Cloudflare Pages.
- The gateway is a separately configured Cloudflare Worker.
- The backend runs in the development environment and requires access to FLOAT/ComfyUI.
- Cloudflare Quick Tunnel URLs can change between runs; the Worker’s `BACKEND_URL` must match the active tunnel URL.
- Network restrictions may prevent a tunnel from connecting. A deployed website does not guarantee that the generation backend is reachable.
- Verify API authentication and gateway configuration before exposing the backend publicly.

## Security

- Do not commit `.env`, API keys, tunnel tokens, or private credentials.
- Keep the backend and gateway configuration aligned.
- Do not expose the backend directly to the public internet without appropriate access controls.
- The actual API security configuration must be verified before claiming that protected endpoints are enabled.

## Development Status

The repository contains an integrated frontend, a FastAPI API, FLOAT integration, and a conversation-generation route. Generation quality, deployment connectivity, and security should be validated in the target environment.

## Contributors

Add the project contributors and their roles here.

## License

No license has been selected in this repository. Review the licensing requirements for FLOAT, ComfyUI, model weights, datasets, and third-party dependencies before distributing the project.
