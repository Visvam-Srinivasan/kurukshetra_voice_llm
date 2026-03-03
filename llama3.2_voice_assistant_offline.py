import os
import queue
import json
import asyncio
import subprocess
import re
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from llama_cpp import Llama
import edge_tts

# -------------------------
# BASE DIRECTORY (NO ABS PATHS)
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000
VOSK_MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-en-us-0.15")
LLAMA_MODEL_PATH = os.path.join(BASE_DIR, "Phi-3-mini-4k-instruct-q4.gguf")
VOICE = "en-IN-NeerjaNeural"

audio_queue = queue.Queue()
is_speaking = False

# -------------------------
# VERIFY FILES EXIST
# -------------------------
if not os.path.isdir(VOSK_MODEL_PATH):
    raise RuntimeError("Vosk model folder not found in project directory.")
if not os.path.isfile(LLAMA_MODEL_PATH):
    raise RuntimeError("Llama GGUF file not found in project directory.")

# -------------------------
# LOAD LLAMA
# -------------------------
print("Loading Llama model...")
llm = Llama(
    model_path=LLAMA_MODEL_PATH,
    n_ctx=512,
    n_threads=os.cpu_count(),
    n_batch=64
)

# -------------------------
# AUDIO CALLBACK
# -------------------------
def audio_callback(indata, frames, time, status):
    global is_speaking
    if not is_speaking:
        audio_queue.put(bytes(indata))

# -------------------------
# CLEAN OUTPUT
# -------------------------
def clean_text(text):
    # Remove markdown bold/italic
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)

    # Strip ANY role/label prefix at the start, e.g. "AI:", "Assistant:", "Bot:"
    text = re.sub(r"(?i)^(ai|assistant|bot|llm|system|user)\s*:\s*", "", text.strip())

    # Remove parenthetical meta-notes e.g. "(Note: ...)", "(Explanation: ...)"
    text = re.sub(
        r"\((?:note|explanation|disclaimer|warning|ai)[^)]*\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Collapse newlines and extra whitespace
    text = re.sub(r"\n+", ". ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------
# LLM RESPONSE
# -------------------------
def generate_text(prompt):
    """
    Prompt is structured so the model returns ONLY a plain spoken reply —
    no role labels, no markdown, no meta-commentary.
    """
    try:
        system_instruction = (
            "You are a helpful voice assistant. "
            "Reply in plain conversational sentences only. "
            "Do NOT start your reply with 'AI:', 'Assistant:', or any label. "
            "Do NOT add notes, disclaimers, or explanations in parentheses."
        )
        full_prompt = (
            f"{system_instruction}\n\n"
            f"User: {prompt}\n"
            f"Assistant:"
        )
        response = llm(
            full_prompt,
            max_tokens=120,
            temperature=0.7,
            stop=["User:", "\nUser", "AI:", "\nAI"]
        )
        text = response["choices"][0]["text"]
        return clean_text(text)
    except Exception as e:
        print("LLM Error:", e)
        return "I encountered an error."

# -------------------------
# EDGE TTS
# -------------------------
def speak(text):
    global is_speaking

    async def _speak_chunk(chunk, filename):
        communicate = edge_tts.Communicate(chunk, VOICE)
        await communicate.save(filename)

    try:
        is_speaking = True
        max_chars = 800
        chunks = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        for i, chunk in enumerate(chunks):
            filename = os.path.join(BASE_DIR, f"response_{i}.mp3")
            asyncio.run(_speak_chunk(chunk, filename))
            subprocess.run(["ffplay", "-autoexit", "-nodisp", filename])
            os.remove(filename)
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
    dtype="int16",
    channels=1,
    callback=audio_callback
):
    while True:
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            user_text = result.get("text", "")
            if not user_text.strip():
                continue
            print("You:", user_text)
            reply = generate_text(user_text)
            print("Assistant:", reply)
            speak(reply)