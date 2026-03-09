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

     - Click **Run**
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

5. In UI, click **Run** and test:

     - Chat prompt: `hello jarvis`
     - Fast query: `what day is today`
     - Obsidian/local memory: `obsidian note review chapter 2 tomorrow`

## TTS + Input Behavior

- UI replies are spoken when `ui_speak_responses = True`
- Voice loop is off by default in UI mode (`enable_voice_loop_in_ui = False`)
- If mic/PyAudio is unavailable and voice input is enabled, Jarvis falls back to keyboard input

## Voice Commands (Websites)

To use voice commands in the GUI:

- Set `enable_voice_loop_in_ui = True` in `Jarvis/config/config.py`
- Keep `voice_input_enabled = True`
- Run `python main.py`, click **Run**, then speak commands like:
     - `open youtube`
     - `open github.com`
     - `go to reddit`
     - `visit stackoverflow.com`

Website commands now normalize plain names and domains before opening.

## Optional Cloud Integrations

You only need API keys/packages if you want cloud features like weather/calendar/email.

- Optional extras install:

    `pip install -r requirements-optional-cloud.txt`

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
        ├── requirements.txt
        └── requirements-optional-cloud.txt

## License

This project is licensed under the [MIT License](LICENSE).
