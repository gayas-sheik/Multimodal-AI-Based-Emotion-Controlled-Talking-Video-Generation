# Multimodal AI-Based Emotion-Controlled Talking Video Generation

Live Demo: SentioGaurd AI
https://sentioguard-ai-web.pages.dev/

## 📌 Project Overview

This project aims to develop a multimodal AI system that generates realistic, emotion-aware talking-face videos using a reference face image and speech audio.

The system will analyse speech audio to identify emotional characteristics and use audio features, facial motion prediction, and deep learning-based video generation techniques to produce a talking video with synchronised lip movements and emotion-related facial expressions.

The goal is to preserve the identity of the person in the reference image while generating natural facial movements that correspond to the input speech.

## 🎯 Objectives

* Develop an audio-processing pipeline to extract meaningful speech features.
* Identify emotional characteristics from speech audio.
* Preprocess video datasets and extract facial information for model training.
* Predict facial movements corresponding to speech.
* Generate talking-face video frames while preserving the reference identity.
* Improve temporal consistency between consecutive frames.
* Synchronise the generated video with the original speech audio.

## ⚙️ Proposed System Workflow

The proposed system follows these stages:

1. **Input Processing:** Accept a reference face image and speech audio.
2. **Audio Preprocessing:** Process the audio and extract relevant acoustic features.
3. **Emotion Recognition:** Estimate emotional characteristics from the speech.
4. **Facial Motion Prediction:** Predict speech-related facial movements.
5. **Video Generation:** Generate facial frames conditioned on the reference image, speech features, and predicted emotional characteristics.
6. **Temporal Consistency:** Reduce unwanted variations between consecutive frames.
7. **Audio-Video Synchronisation:** Combine the generated frames with the original audio.
8. **Output:** Produce an emotion-aware talking-face video.

## 🧠 Technologies

The following technologies are planned for the project:

* **Programming Language:** Python
* **Deep Learning Framework:** PyTorch
* **Computer Vision:** OpenCV
* **Audio Processing:** Librosa, NumPy
* **Video Processing:** FFmpeg
* **Data Analysis:** Pandas, Scikit-learn
* **Version Control:** Git and GitHub

The final technology stack may change during implementation.

## 🗂️ Planned Project Structure

```text
Multimodal-AI-Based-Emotion-Controlled-Talking-Video-Generation/
│
├── README.md
├── .gitignore
├── requirements.txt
├── configs/
├── data/
├── checkpoints/
├── scripts/
├── src/
│   ├── audio_processing/
│   ├── emotion_recognition/
│   ├── video_preprocessing/
│   ├── facial_motion/
│   └── video_generation/
├── tests/
└── outputs/
```

This is the proposed structure. Directories and modules will be added as development progresses.

## 📊 Dataset and Training

The project will require suitable audio-video datasets containing speech recordings and corresponding facial movements. Emotion-labelled data will be used where available and appropriate.

Planned data preparation tasks include:

* Audio preprocessing and feature extraction.
* Video frame extraction and resizing.
* Face detection and alignment.
* Audio-video temporal synchronisation.
* Emotion label preparation.
* Training, validation, and test dataset splitting.

Dataset selection, model architecture, and training configurations will be finalised during development.

## 🚀 Expected Outcome

The intended outcome is a web-based AI application that accepts a reference face image and speech audio and generates a talking-face video with:

* Speech-synchronised lip movements.
* Emotion-related facial expressions inferred from audio.
* Preservation of the reference person's facial identity.
* Temporally consistent generated frames.
* An output video containing the original speech audio.

These are project goals; the final performance and capabilities will be evaluated after implementation and testing.

## 🔬 Development Status

**Status:** Initial development and research phase.

Current and upcoming work includes:

* Literature review and model research.
* Dataset identification and preprocessing.
* Audio feature extraction and emotion recognition.
* Facial motion prediction.
* Talking-face video generation.
* Model evaluation and system integration.

## 👥 Contributors

Add the names of the project team members here.

## 📄 License

No license has been selected yet. Usage and distribution terms will be determined in accordance with the project's requirements and applicable dataset and model licenses.
