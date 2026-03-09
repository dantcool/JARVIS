import datetime
import json
import os
import re
import threading
import time


MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "user_memory.json")
MEMORY_LOCK = threading.Lock()


def load_user_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except Exception as error:
        print(f"Memory read error: {error}")
    return {}


def save_user_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2)
        return True
    except Exception as error:
        print(f"Memory write error: {error}")
        return False


def set_user_name(name):
    cleaned = name.strip().strip(".?!,")
    if not cleaned:
        return False

    with MEMORY_LOCK:
        memory = load_user_memory()
        memory["name"] = cleaned
        return save_user_memory(memory)


def get_user_name():
    with MEMORY_LOCK:
        memory = load_user_memory()
        return memory.get("name")


def try_handle_memory_command(question):
    text = question.lower().strip()

    remember_patterns = [
        r"^remember my name is\s+(.+)$",
        r"^my name is\s+(.+)$",
        r"^remember that my name is\s+(.+)$",
    ]
    for pattern in remember_patterns:
        match = re.match(pattern, text)
        if match:
            name = match.group(1).strip()
            if set_user_name(name):
                return f"Got it. I'll remember your name is {name}."
            return "I couldn't save your name just now."

    if text in {"what is my name", "what's my name", "do you remember my name"}:
        name = get_user_name()
        if name:
            return f"Your name is {name}."
        return "I don't know your name yet. Say: remember my name is <your name>."

    return None


def try_handle_fast_local_query(assistant, question):
    text = question.lower().strip()

    day_phrases = [
        "what day is it",
        "what day is today",
        "which day is it",
        "what weekday is it",
        "day is it",
        "weekday",
    ]
    if any(phrase in text for phrase in day_phrases):
        weekday = datetime.datetime.now().strftime("%A")
        return f"Today is {weekday}."

    date_phrases = [
        "what is the date",
        "what's the date",
        "today's date",
        "todays date",
    ]
    if any(phrase in text for phrase in date_phrases):
        return assistant.tell_me_date()

    time_phrases = [
        "what time is it",
        "current time",
        "tell me the time",
    ]
    if any(phrase in text for phrase in time_phrases):
        time_c = assistant.tell_time()
        return f"Sir the time is {time_c}"

    return None


def ask_local_llm(assistant, question):
    memory_reply = try_handle_memory_command(question)
    if memory_reply:
        return memory_reply

    fast_reply = try_handle_fast_local_query(assistant, question)
    if fast_reply:
        return fast_reply

    known_name = get_user_name()
    if known_name:
        question = (
            f"User profile: the user's name is {known_name}. "
            f"Use it naturally when helpful.\n\nUser: {question}"
        )

    stop_event = threading.Event()

    def progress_indicator():
        print("Jarvis: thinking", end="", flush=True)
        while not stop_event.wait(1.0):
            print(".", end="", flush=True)

    indicator_thread = threading.Thread(target=progress_indicator, daemon=True)
    indicator_thread.start()
    started_at = time.time()

    try:
        answer = assistant.ask_ollama(question)
        elapsed = time.time() - started_at
        stop_event.set()
        indicator_thread.join(timeout=0.2)
        print(f" done ({elapsed:.1f}s)")
        if answer:
            print(answer)
            return answer
    except Exception as error:
        elapsed = time.time() - started_at
        stop_event.set()
        indicator_thread.join(timeout=0.2)
        print(f" failed ({elapsed:.1f}s)")
        print(f"Ollama error: {error}")

    return "Sorry sir, I couldn't get a response from your local Ollama model."


def computational_intelligence(assistant, question):
    return ask_local_llm(assistant, question)
