Voice Assistant (Vosk + Gemini + Edge TTS)

A real-time voice assistant using:

Vosk (offline speech-to-text)

Google Gemini API (LLM)

Edge TTS (text-to-speech)

SoundDevice (microphone input)

Flow:
Microphone → Vosk → Gemini → Edge TTS → Speaker

Requirements

Python 3.9+

Working microphone

Internet connection (for Gemini and Edge TTS)

FFmpeg installed (for ffplay)

1. Setup Project

Create a project folder and place your test_tts.py file inside it.

Optional (recommended) virtual environment:

Windows:
python -m venv venv
venv\Scripts\activate

Linux/macOS:
python -m venv venv
source venv/bin/activate

2. Install Dependencies

pip install sounddevice vosk python-dotenv google-generativeai edge-tts

3. Install FFmpeg

Required for audio playback.

Ubuntu/Debian:
sudo apt install ffmpeg

Windows:
Download from ffmpeg.org and add the bin folder to PATH.

Verify:
ffplay -version

4. Download Vosk Model

Download:
vosk-model-small-en-us-0.15

From:
https://alphacephei.com/vosk/models

Extract it inside your project folder.

Your structure should be:

voice-assistant/

test_tts.py

.env

vosk-model-small-en-us-0.15/

5. Setup Gemini API

Go to https://aistudio.google.com

Create an API key

Copy the key

Create a .env file in your project folder:

GOOGLE_API_KEY=your_actual_api_key_here

Do not share or commit this file.

6. Run the Assistant

python test_tts.py

You should see:

Loading Vosk...
Listening... Press Ctrl+C to exit.

Speak into the microphone to interact.

Common Issues

429 RESOURCE_EXHAUSTED
Free tier limit is 20 requests/day. Wait 24 hours or enable billing.

No audio
Make sure ffplay is installed and available in PATH.

Vosk model error
Ensure the folder name matches:
vosk-model-small-en-us-0.15

Notes

Vosk runs fully offline.

Gemini requires internet and has quota limits.

Edge TTS requires internet.

The code cleans markdown before speech output.
