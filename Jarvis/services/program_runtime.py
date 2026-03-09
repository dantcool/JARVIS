import datetime


def startup(speak, assistant, force_local_chat_mode, enable_voice_loop_in_ui, voice_input_enabled):
    speak("Initializing Jarvis runtime")
    speak("Loading local assistant modules")

    if force_local_chat_mode:
        speak("Local model mode is active")
    else:
        speak("Hybrid assistant mode is active")

    if enable_voice_loop_in_ui and voice_input_enabled:
        speak("Voice input is enabled")
    else:
        speak("Voice input is off. Use chat input in the UI")

    hour = int(datetime.datetime.now().hour)
    if 0 <= hour <= 12:
        speak("Good morning")
    elif 12 < hour < 18:
        speak("Good afternoon")
    else:
        speak("Good evening")

    c_time = assistant.tell_time()
    speak(f"Current time is {c_time}")
    speak("Jarvis is online and ready")
