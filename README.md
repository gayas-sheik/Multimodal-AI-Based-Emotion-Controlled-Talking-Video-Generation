# SentioGaurdAI

**Multimodal AI-Based Emotion-Controlled Talking Video Generation**

SentioGaurdAI generates emotionally expressive talking-head videos using a reference face image, speech audio and a selected emotion.

## Architecture

- Frontend: Next.js, React and Tailwind CSS
- Backend: FastAPI
- AI Generation: FLOAT through ComfyUI
- Inference: Local NVIDIA GPU
- Frontend Hosting: Cloudflare Pages
- API Gateway: Cloudflare Workers
- Secure Backend Connectivity: Cloudflare Tunnel

## Project Structure

```text
SentioGaurdAI/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
├── workflows/
│   └── float_api.json
├── .env.example
├── .gitignore
└── SentioGaurdAI.bat
```

ComfyUI, model weights, virtual environments and generated media are maintained locally.

## Requirements

- Windows 10/11
- Python 3.12
- Node.js and npm
- NVIDIA GPU with compatible CUDA/PyTorch support
- ComfyUI with FLOAT
- FFmpeg
- Cloudflared for public backend access

## Local Setup

### 1. Configure environment variables

Copy `.env.example` to `.env` and configure your own API secret.

```env
COMFYUI_URL=http://127.0.0.1:8188
FLOAT_API_KEY=your_random_secret
```

Never commit `.env` or expose your API secret.

### 2. Install backend dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### 3. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

### 4. Configure ComfyUI

Install ComfyUI, the FLOAT custom node, its dependencies and required model weights. Configure the workflow before starting the application.

### 5. Start the application

Run `SentioGaurdAI.bat`.

## Cloud Deployment

- Frontend: Cloudflare Pages
- API gateway: Cloudflare Workers
- Local inference backend: FastAPI
- Secure connection: Cloudflare Tunnel

The local GPU machine must remain online while visitors generate videos.

Quick Tunnel URLs change when restarted, so the Worker backend URL must be updated accordingly.

## Security

- Backend API secret is stored in the local `.env` file and Cloudflare Worker secrets.
- The frontend does not contain the backend API secret.
- ComfyUI is not exposed directly to the internet.
- Backend upload size validation is enabled.
- Public deployments should implement visitor rate limiting and abuse protection.

## Generation Workflow

1. Upload a reference face image.
2. Upload speech audio.
3. Select an emotion and generation settings.
4. Submit the generation request.
5. FLOAT processes the inputs through ComfyUI.
6. Retrieve the generated talking-head video.

## Project Focus

Multimodal AI, image analysis, pattern recognition and emotional talking-head generation.
