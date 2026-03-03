================================================================================
                        VOICE ASSISTANT - SETUP & RUN GUIDE
                        Linux (Ubuntu/Debian-based distros)
================================================================================

--------------------------------------------------------------------------------
OVERVIEW
--------------------------------------------------------------------------------
This is an offline voice assistant that runs entirely on your local machine.
It uses:
  - Vosk        : Offline speech recognition (speech -> text)
  - Phi-3 Mini  : Local LLM via llama-cpp-python (text -> response)
  - Edge TTS    : Microsoft neural text-to-speech (response -> audio)
  - ffplay      : Audio playback (part of ffmpeg)
  - sounddevice : Microphone input

--------------------------------------------------------------------------------
REQUIRED DIRECTORY STRUCTURE
--------------------------------------------------------------------------------
All files must live in the same folder. Final layout should look like this:

    your-project-folder/
    |
    |-- VA.py
    |-- vosk-model-small-en-us-0.15/       <-- extracted Vosk model folder
    |   |-- am/
    |   |-- conf/
    |   |-- graph/
    |   |-- ivector/
    |   `-- ... (other model files)
    |
    `-- Phi-3-mini-4k-instruct-q4.gguf     <-- downloaded GGUF model file

--------------------------------------------------------------------------------
STEP 1 - SYSTEM DEPENDENCIES
--------------------------------------------------------------------------------
Open a terminal and run:

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-pip python3-venv \
        ffmpeg portaudio19-dev build-essential \
        libportaudio2 libasound-dev

Verify Python is 3.9 or higher:

    python3 --version

--------------------------------------------------------------------------------
STEP 2 - CREATE A VIRTUAL ENVIRONMENT
--------------------------------------------------------------------------------
Navigate to your project folder, then:

    cd /path/to/your-project-folder
    python3 -m venv venv
    source venv/bin/activate

You should now see (venv) at the start of your terminal prompt.
Always activate this environment before running the assistant.

--------------------------------------------------------------------------------
STEP 3 - INSTALL PYTHON PACKAGES
--------------------------------------------------------------------------------
With the virtual environment active, install all required packages:

    pip install --upgrade pip
    pip install vosk sounddevice edge-tts

Install llama-cpp-python (CPU build):

    pip install llama-cpp-python

    NOTE: If you have a CUDA-compatible NVIDIA GPU and want GPU acceleration,
    use this command instead (requires CUDA toolkit installed):

        CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall

--------------------------------------------------------------------------------
STEP 4 - DOWNLOAD THE VOSK SPEECH RECOGNITION MODEL
--------------------------------------------------------------------------------
Option A - Using wget:

    cd /path/to/your-project-folder
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip

Option B - Manual download:
    1. Go to: https://alphacephei.com/vosk/models
    2. Download: vosk-model-small-en-us-0.15.zip
    3. Extract the zip into your project folder
    4. The extracted folder must be named: vosk-model-small-en-us-0.15

After extraction, confirm the folder exists:

    ls vosk-model-small-en-us-0.15/

You should see subfolders like: am  conf  graph  ivector

--------------------------------------------------------------------------------
STEP 5 - DOWNLOAD THE PHI-3 MINI LLM (GGUF FORMAT)
--------------------------------------------------------------------------------
Option A - Using wget:

    cd /path/to/your-project-folder
    wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

Option B - Manual download:
    1. Go to: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
    2. Click the Files tab
    3. Download: Phi-3-mini-4k-instruct-q4.gguf
    4. Place it directly in your project folder (not inside a subfolder)

    NOTE: This file is approximately 2.2 GB. Ensure you have enough disk space.

After download, confirm the file exists:

    ls -lh Phi-3-mini-4k-instruct-q4.gguf

--------------------------------------------------------------------------------
STEP 6 - VERIFY YOUR MICROPHONE
--------------------------------------------------------------------------------
Check that your microphone is detected:

    python3 -c "import sounddevice as sd; print(sd.query_devices())"

You should see your microphone listed. If nothing appears, check:
  - sudo apt install pulseaudio
  - Ensure the microphone is plugged in and not muted
  - Run: alsamixer   (use arrow keys to unmute and raise mic volume)

--------------------------------------------------------------------------------
STEP 7 - PLACE VA.py IN THE PROJECT FOLDER
--------------------------------------------------------------------------------
Copy or move VA.py into your project folder:

    /path/to/your-project-folder/VA.py

Double-check the final folder layout matches the structure shown at the top
of this file.

--------------------------------------------------------------------------------
STEP 8 - RUN THE ASSISTANT
--------------------------------------------------------------------------------
Make sure your virtual environment is active:

    source venv/bin/activate

Then run:

    python3 VA.py

You will see:
    Loading Llama model...
    Loading Vosk...
    Listening... Press Ctrl+C to exit.

Speak into your microphone. The assistant will:
  1. Transcribe your speech
  2. Generate a reply using the local LLM
  3. Speak the reply aloud using Edge TTS

Press Ctrl+C at any time to stop.

--------------------------------------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------------------------------------

Problem : "Vosk model folder not found"
Fix     : Make sure the folder vosk-model-small-en-us-0.15 is in the same
          directory as VA.py and the name matches exactly (case-sensitive).

Problem : "Llama GGUF file not found"
Fix     : Make sure Phi-3-mini-4k-instruct-q4.gguf is in the same directory
          as VA.py.

Problem : "ffplay: command not found"
Fix     : sudo apt install ffmpeg

Problem : No audio output
Fix     : Check speaker/headphone volume. Test ffplay with:
              ffplay -autoexit /usr/share/sounds/alsa/Front_Left.wav

Problem : PortAudio or sounddevice errors
Fix     : sudo apt install portaudio19-dev libportaudio2
          Then reinstall: pip install sounddevice

Problem : Edge TTS fails or gives network error
Fix     : Edge TTS requires an internet connection to generate audio.
          Check your internet and firewall settings.

Problem : LLM is very slow
Fix     : Reduce max_tokens in generate_text(), or use a smaller GGUF model.
          For GPU acceleration see the CUDA install note in Step 3.

Problem : "ModuleNotFoundError" for any package
Fix     : Make sure your virtual environment is active:
              source venv/bin/activate
          Then reinstall the missing package with pip.

--------------------------------------------------------------------------------
QUICK REFERENCE - ALL COMMANDS IN ORDER
--------------------------------------------------------------------------------

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-pip python3-venv ffmpeg \
        portaudio19-dev build-essential libportaudio2 libasound-dev

    mkdir voice-assistant && cd voice-assistant

    python3 -m venv venv
    source venv/bin/activate

    pip install --upgrade pip
    pip install vosk sounddevice edge-tts llama-cpp-python

    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip

    wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

    # Copy VA.py into this folder, then:
    python3 VA.py

================================================================================