# agle-transcriber
# AGLE Web Commerce Automated Transcription Tool

This repository provides an end-to-end automation stack containing:
1. **FastAPI Backend** with an integrated speech-to-text model (OpenAI Whisper) and formatting guidelines rule engine.
2. **Playwright Bot** to auto-claim tasks, download audio streams, format transcripts, and submit them securely.
3. **Frontend Dashboard** to control and monitor the automation engine in real time.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install
   
