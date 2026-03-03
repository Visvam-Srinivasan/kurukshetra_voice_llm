import os
import queue
import sys
import json
import asyncio
import sounddevice as sd
import subprocess
import threading

from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
from google import genai
from google.genai import types
import edge_tts

# -------------------------
# LOAD ENV VARIABLES
# -------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    print("GOOGLE_API_KEY not found in .env file")
    sys.exit(1)

# -------------------------
# SETTINGS
# -------------------------

SAMPLE_RATE = 16000
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"

LLM_MODEL = "models/gemini-2.5-flash"
VOICE = "en-IN-NeerjaNeural"

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

audio_queue = queue.Queue()
is_speaking = False   # 🔥 Important flag

# -------------------------
# AUDIO CALLBACK
# -------------------------

def audio_callback(indata, frames, time, status):
    global is_speaking

    if status:
        print(status, file=sys.stderr)

    # 🔥 Ignore mic input while speaking
    if not is_speaking:
        audio_queue.put(bytes(indata))

# -------------------------
# GEMINI TEXT RESPONSE
# -------------------------

import re

def clean_text_for_speech(text):
    if not text:
        return ""

    # Remove markdown bold/italic
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Remove bullet points
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)

    # Remove extra newlines
    text = re.sub(r"\n+", ". ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def generate_text(prompt):
    try:
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=400
            )
        )

        # SAFER extraction
        full_text = ""
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    full_text += part.text

        cleaned = clean_text_for_speech(full_text)

        return cleaned

    except Exception as e:
        print("Gemini LLM Error:", e)
        return "Sorry, I encountered an error."

# -------------------------
# EDGE TTS
# -------------------------

def speak_with_edge(text):
    global is_speaking

    async def _speak_chunk(chunk, filename):
        communicate = edge_tts.Communicate(chunk, VOICE)
        await communicate.save(filename)

    try:
        is_speaking = True

        # Split long text into chunks (safe length)
        max_chars = 800
        chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

        for i, chunk in enumerate(chunks):
            filename = f"response_{i}.mp3"
            asyncio.run(_speak_chunk(chunk, filename))

            subprocess.run([
                "ffplay",
                "-autoexit",
                "-nodisp",
                filename
            ])

    except Exception as e:
        print("Edge TTS Error:", e)

    finally:
        is_speaking = False

# -------------------------
# LOAD VOSK
# -------------------------

print("Loading Vosk...")
vosk_model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)

print("Listening... Press Ctrl+C to exit.")

# -------------------------
# MAIN LOOP
# -------------------------

with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=4000,
    dtype='int16',
    channels=1,
    callback=audio_callback
):
    while True:
        data = audio_queue.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            user_text = result.get("text", "")

            if user_text.strip() == "":
                continue

            print("You:", user_text)

            reply = generate_text(user_text)
            print("Assistant:", reply)

            speak_with_edge(reply)