# JARVIS (Local Ollama Edition)

This project is a local-first JARVIS-style desktop assistant.
It runs with a GUI window, supports typed chat, and uses Ollama on your machine.

## What’s Updated

- Main interaction is now in the **Jarvis GUI window** (`main.py`)
- You can type directly to Jarvis in the UI chat box
- Terminal is used for **event logging/debug output**
- Ollama integration supports both `/api/chat` and fallback `/api/generate`
- Local user memory added (`remember my name is ...`)
- TTS fixed and enabled for UI responses
- API keys are optional for cloud features; local mode works without them

## Quick Start (Recommended)

1. Install dependencies:

     `pip install -r requirements.txt`

2. Confirm Ollama is running:

     - If already running, do nothing
     - If not running, start once: `ollama serve`

3. Ensure a model is available (example):

     `ollama pull llama4:latest`

4. Launch Jarvis UI:

     `python main.py`

5. In the window:

     - Jarvis starts automatically
     - Type in the chat box
     - Press **Send**

## Install Ollama

Install Ollama first (one-time setup):

- **Windows**
     - Download and install from: `https://ollama.com/download/windows`
     - After install, open a new terminal and verify:
          - `ollama --version`

- **macOS**
     - Download installer from: `https://ollama.com/download/mac`
     - Or with Homebrew:
          - `brew install ollama`

- **Linux**
     - Install with the official script:
          - `curl -fsSL https://ollama.com/install.sh | sh`

Start the local Ollama server when needed:

- `ollama serve`

List local models:

- `ollama list`

## Model Guide (By GPU)

Use this as a quick reference for model size vs VRAM.

- **8 GB VRAM (entry/mid GPU)**
     - Good starting models: `qwen2.5:7b`, `llama3.1:8b`
     - Pull example: `ollama pull qwen2.5:7b`

- **12–16 GB VRAM (strong mid/high GPU)**
     - Good balance: `qwen2.5:14b`, `llama3.1:8b` (higher context)
     - Pull example: `ollama pull qwen2.5:14b`

- **20–24 GB VRAM (RTX 4090 class)**
     - Higher quality local chat: `qwen2.5:32b` or keep `llama4:latest` if stable on your setup
     - Pull example: `ollama pull qwen2.5:32b`

- **CPU-only or low VRAM fallback**
     - Lighter model: `phi3:mini`
     - Pull example: `ollama pull phi3:mini`

After choosing a model, set it in `Jarvis/config/config.py`:

- `ollama_model = "<model-tag>"`

Tip: if responses are slow or you hit memory errors, use a smaller model first, then scale up.

## Current Config Defaults

File: `Jarvis/config/config.py`

- `ollama_auto_select_model = True` (auto-picks best available local model)

## Memory (Local)


Auto-select behavior:

- If `ollama_auto_select_model = True`, Jarvis checks your installed local models and uses the best available one (largest parameter size, then model size).
- If your configured `ollama_model` exists locally, Jarvis prefers that exact model.
- Set `ollama_auto_select_model = False` to force only your configured `ollama_model`.

- `remember my name is <your name>`
- `what is my name`

Stored in: `user_memory.json` (project root)

## Obsidian Learning Notes

Obsidian is **optional**. Jarvis can run without it and store learning notes locally.

As your usage and note volume grow, Obsidian is **recommended** for better long-term organization and review.

1. Set your vault path in `Jarvis/config/config.py`:

     `obsidian_vault_path = "C:/Users/<you>/Documents/YourVault"`

2. Use commands like:

     - `obsidian note python decorators are functions wrapping functions`
     - `save to obsidian review chapter 4 tomorrow`
     - `open obsidian notes`
     - `review obsidian notes`

Jarvis writes to: `<vault>/<obsidian_notes_folder>/<obsidian_memory_note>`

If no vault path is set, Jarvis writes to local fallback memory:

- default: `learning_memory.md` in project root
- optional override: `local_learning_note_path` in config

## Guest User Test Checklist

For first-time testing on a clean machine:

1. Install dependencies:

     `pip install -r requirements.txt`

2. Start Ollama (or confirm it is already running):

     `ollama serve`

3. Pull the configured model if needed:

     `ollama pull llama4:latest`

4. Run Jarvis:

     `python main.py`

5. In UI, Jarvis starts automatically. Test:

     - Chat prompt: `hello jarvis`
     - Fast query: `what day is today`
     - Obsidian/local memory: `obsidian note review chapter 2 tomorrow`

## TTS + Input Behavior

- UI replies are spoken when `ui_speak_responses = True`
- Voice loop is disabled by default in UI mode (`enable_voice_loop_in_ui = False`)
- If microphone capture is unavailable and voice input is enabled, Jarvis falls back to keyboard input
- Use the `Voice Input` button in the UI to capture one voice command on demand
- UI status now shows `Idle`, `Listening`, `Executing`, `Thinking`, or `Error`

## Voice Input Setup (Windows)

Voice input now works without PyAudio by default using `SpeechRecognition` + `sounddevice`.

1. Install dependencies:

     `pip install -r requirements.txt`

2. Default backend (recommended):

     - `voice_input_backend = "sounddevice"`

3. Optional fallback backend:

     - `voice_input_backend = "pyaudio"` (only if PyAudio is installed and working)

4. If you want to try PyAudio anyway:

     `python -m pip install --upgrade pip setuptools wheel`

     `pip install PyAudio`

5. Tune microphone settings in `Jarvis/config/config.py` if needed:

     - `microphone_device_index = None` (default device)
     - `microphone_timeout = 5`
     - `microphone_phrase_time_limit = 10`
     - `microphone_adjust_for_ambient = True`
     - `microphone_ambient_duration = 0.8`
     - `voice_sample_rate = 16000`
     - `voice_recognition_language = "en-US"`

6. Ensure voice is enabled:

     - `voice_input_enabled = True`
     - `enable_voice_loop_in_ui = False` (recommended with the Voice Input button)

If speech is not detected, increase `microphone_timeout` and `microphone_phrase_time_limit`, then retry.

In the UI, use the `Microphone` dropdown and `Scan` button to select the exact input device before pressing `Voice Input`.

## Voice Commands (Websites)

To use voice commands in the GUI:

- Set `enable_voice_loop_in_ui = True` in `Jarvis/config/config.py`
- Keep `voice_input_enabled = True`
- Run `python main.py`, then speak commands like:
     - `open youtube`
     - `open github.com`
     - `go to reddit`
     - `visit stackoverflow.com`

Website commands now normalize plain names and domains before opening.

## Web Search Commands

Jarvis can now open a browser and run web searches directly from chat or voice input.

Try commands like:

- `search google for python dataclasses`
- `search web for best sqlite gui`
- `web search for local llm benchmarks`
- `google weather in new york`
- `search for pyqt threading examples`

## Troubleshooting

- `bind: Only one usage of each socket address...` on `ollama serve`
    - Ollama is already running on port `11434`
- `404 ... /api/chat`
    - Handled by fallback to `/api/generate` in current code
- No model response
    - Check `ollama list`
    - Ensure `ollama_model` in config matches an installed model

## Project Layout

        ├── Jarvis/
        │   ├── config/
        │   ├── features/
        │   └── utils/
        ├── main.py
     └── requirements.txt

## License

This project is licensed under the [MIT License](LICENSE).
