force_local_chat_mode = True
voice_input_enabled = True
voice_input_backend = "sounddevice"
voice_retry_limit = 2
keyboard_fallback = True
enable_voice_loop_in_ui = False
microphone_device_index = None
microphone_timeout = 5
microphone_phrase_time_limit = 10
microphone_adjust_for_ambient = True
microphone_ambient_duration = 0.8
voice_sample_rate = 16000
voice_recognition_language = "en-US"
voice_energy_threshold = 300
voice_dynamic_energy_threshold = True
ui_speak_responses = True
tts_enabled = True
tts_rate = 175
tts_voice_index = 0

ollama_url = "http://127.0.0.1:11434"
ollama_model = "llama4:latest"
ollama_auto_select_model = True
ollama_auto_route_by_prompt = True
ollama_model_candidates = [
	"qwen2.5:7b",
	"llama3.2:latest",
	"llama4:latest",
]
ollama_timeout = 120
ollama_connect_timeout = 5
ollama_model_discovery_timeout = 5
ollama_system_prompt = "You are Jarvis, a concise and helpful local AI assistant."
ollama_num_gpu = -1
ollama_num_ctx = 8192
ollama_temperature = 0.6
ollama_num_thread = 0

obsidian_enabled = True
obsidian_vault_path = ""
obsidian_notes_folder = "Jarvis"
obsidian_memory_note = "Jarvis Learning Memory.md"
obsidian_open_after_write = True
local_learning_note_path = ""
