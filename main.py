from Jarvis import JarvisAssistant
import re
import os
import json
import datetime
import sys
import time
import threading
try:
    import wolframalpha
except Exception:
    wolframalpha = None
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton
from Jarvis.features.gui import Ui_MainWindow
from Jarvis.features.command_router import CommandRouter
from Jarvis.config import config

obj = JarvisAssistant()
LOCAL_ONLY_MODE = getattr(config, "local_only_mode", True)
FORCE_LOCAL_CHAT_MODE = getattr(config, "force_local_chat_mode", True)
ENABLE_VOICE_LOOP_IN_UI = getattr(config, "enable_voice_loop_in_ui", False)
UI_SPEAK_RESPONSES = getattr(config, "ui_speak_responses", False)

# ================================ MEMORY ===========================================================================================================

GREETINGS = ["hello jarvis", "jarvis", "wake up jarvis", "you there jarvis", "time to work jarvis", "hey jarvis",
             "ok jarvis", "are you there"]
GREETINGS_RES = ["always there for you sir", "i am ready sir",
                 "your wish my command", "how can i help you sir?", "i am online and ready sir"]

DEFAULT_CONTACT_EMAIL = getattr(config, "default_contact_email", "")

EMAIL_DIC = {
    'myself': DEFAULT_CONTACT_EMAIL,
    'my official email': DEFAULT_CONTACT_EMAIL,
    'my second email': DEFAULT_CONTACT_EMAIL,
    'my official mail': DEFAULT_CONTACT_EMAIL,
    'my second mail': DEFAULT_CONTACT_EMAIL
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "user_memory.json")
MEMORY_LOCK = threading.Lock()
# =======================================================================================================================================================


def speak(text):
    if text:
        print(f"Jarvis: {text}")
    obj.tts(text)


app_id = config.wolframalpha_id


def load_user_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as error:
        print(f"Memory read error: {error}")
    return {}


def save_user_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
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


def try_handle_fast_local_query(question):
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
        return obj.tell_me_date()

    time_phrases = [
        "what time is it",
        "current time",
        "tell me the time",
    ]
    if any(phrase in text for phrase in time_phrases):
        time_c = obj.tell_time()
        return f"Sir the time is {time_c}"

    return None


def ask_local_llm(question):
    memory_reply = try_handle_memory_command(question)
    if memory_reply:
        return memory_reply

    fast_reply = try_handle_fast_local_query(question)
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
        answer = obj.ask_ollama(question)
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


def local_mode_blocked(service_name):
    speak(
        f"{service_name} is disabled in local only mode. "
        "If you want it, set local_only_mode to False in config."
    )


def computational_intelligence(question):
    if not wolframalpha or not app_id or "<your_" in str(app_id):
        return ask_local_llm(question)

    try:
        client = wolframalpha.Client(app_id)
        answer = client.query(question)
        answer = next(answer.results).text
        print(answer)
        return answer
    except:
        return ask_local_llm(question)
    
def startup():
    speak("Initializing Jarvis")
    speak("Starting all systems applications")
    speak("Installing and checking all drivers")
    speak("Caliberating and examining all the core processors")
    speak("Checking the internet connection")
    speak("Wait a moment sir")
    speak("All drivers are up and running")
    speak("All systems have been activated")
    speak("Now I am online")
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        speak("Good Morning")
    elif hour>12 and hour<18:
        speak("Good afternoon")
    else:
        speak("Good evening")
    c_time = obj.tell_time()
    speak(f"Currently it is {c_time}")
    speak("I am Jarvis. Online and ready sir. Please tell me how may I help you")
    



class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()

    def run(self):
        self.TaskExecution()

    def TaskExecution(self):
        startup()
        router = CommandRouter(
            assistant=obj,
            speak=speak,
            config=config,
            local_only_mode=LOCAL_ONLY_MODE,
            local_mode_blocked=local_mode_blocked,
            computational_intelligence=computational_intelligence,
            ask_local_llm=ask_local_llm,
            greetings=GREETINGS,
            greeting_responses=GREETINGS_RES,
            email_dict=EMAIL_DIC,
            calendar_phrases=CALENDAR_STRS,
        )

        while True:
            command = obj.mic_input()
            if not command:
                continue
            command = command.lower().strip()

            if command in {"goodbye", "offline", "bye", "exit", "quit"}:
                speak("Alright sir, going offline. It was nice working with you")
                sys.exit()

            handled = router.route(command)
            if handled:
                continue

            if FORCE_LOCAL_CHAT_MODE:
                answer = ask_local_llm(command)
                speak(answer)
                continue

            answer = ask_local_llm(command)
            speak(answer)


startExecution = MainThread()


class OllamaUiWorker(QThread):
    response_ready = pyqtSignal(str)
    response_error = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = ask_local_llm(self.prompt)
            if not response:
                response = "I received an empty response from the model."
            self.response_ready.emit(response)
        except Exception as error:
            self.response_error.emit(str(error))


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.started = False
        self.ui_router = CommandRouter(
            assistant=obj,
            speak=speak,
            config=config,
            local_only_mode=LOCAL_ONLY_MODE,
            local_mode_blocked=local_mode_blocked,
            computational_intelligence=computational_intelligence,
            ask_local_llm=ask_local_llm,
            greetings=GREETINGS,
            greeting_responses=GREETINGS_RES,
            email_dict=EMAIL_DIC,
            calendar_phrases=CALENDAR_STRS,
        )
        self.chat_worker = None
        self.clock_timer = None
        self.setup_chat_controls()
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)

    def __del__(self):
        sys.stdout = sys.__stdout__

    def setup_chat_controls(self):
        self.chat_input = QLineEdit(self.ui.centralwidget)
        self.chat_input.setGeometry(QtCore.QRect(1000, 450, 300, 41))
        self.chat_input.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")

        self.send_button = QPushButton(self.ui.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(1310, 450, 121, 41))
        self.send_button.setStyleSheet("background-color: rgb(0, 170, 255);\nfont: 75 12pt \"MS Shell Dlg 2\";")
        self.send_button.setText("Send")

        self.send_button.clicked.connect(self.send_ui_message)
        self.chat_input.returnPressed.connect(self.send_ui_message)
        self.ui.textBrowser_3.append("Jarvis UI chat ready. Click Run, then type and press Send.")
        self.set_chat_controls_enabled(False)

    def append_ui_chat(self, speaker, message):
        self.ui.textBrowser_3.append(f"{speaker}: {message}")

    def set_chat_controls_enabled(self, enabled):
        self.chat_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    def send_ui_message(self):
        if not self.started:
            self.append_ui_chat("System", "Please click Run first.")
            return

        if self.chat_worker and self.chat_worker.isRunning():
            return

        prompt = self.chat_input.text().strip()
        if not prompt:
            return

        self.append_ui_chat("You", prompt)
        print(f"[UI] User prompt: {prompt}")
        self.chat_input.clear()

        normalized = prompt.lower().strip()
        if normalized in {"goodbye", "offline", "bye", "exit", "quit"}:
            self.append_ui_chat("Jarvis", "Goodbye sir.")
            self.close()
            return

        handled = self.ui_router.route(normalized)
        if handled:
            self.append_ui_chat("Jarvis", "Task completed.")
            self.chat_input.setPlaceholderText("Type a message to Jarvis...")
            self.set_chat_controls_enabled(True)
            self.chat_input.setFocus()
            return

        self.chat_input.setPlaceholderText("Jarvis is thinking...")
        self.set_chat_controls_enabled(False)

        self.chat_worker = OllamaUiWorker(prompt)
        self.chat_worker.response_ready.connect(self.on_ui_response)
        self.chat_worker.response_error.connect(self.on_ui_error)
        self.chat_worker.start()

    def on_ui_response(self, response):
        self.append_ui_chat("Jarvis", response)
        print("[UI] Jarvis response received")
        if UI_SPEAK_RESPONSES:
            speak(response)
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")
        self.set_chat_controls_enabled(True)
        self.chat_input.setFocus()

    def on_ui_error(self, error):
        msg = f"Could not reach local Ollama: {error}"
        self.append_ui_chat("Jarvis", msg)
        print(f"[UI] Error: {error}")
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")
        self.set_chat_controls_enabled(True)
        self.chat_input.setFocus()

    # def run(self):
    #     self.TaskExection
    def startTask(self):
        if self.started:
            return

        self.started = True
        self.ui.movie = QtGui.QMovie("Jarvis/utils/images/live_wallpaper.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("Jarvis/utils/images/initiating.gif")
        self.ui.label_2.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.showTime)
        self.clock_timer.start(1000)
        self.set_chat_controls_enabled(True)
        self.chat_input.setFocus()

        if ENABLE_VOICE_LOOP_IN_UI:
            if not startExecution.isRunning():
                print("[UI] Starting voice command loop")
                startExecution.start()
        else:
            print("[UI] Voice loop disabled; using UI text chat")
            self.append_ui_chat("System", "Voice loop disabled. Use the chat box to talk to Jarvis.")

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)
        self.ui.textBrowser_2.setText(label_time)


app = QApplication(sys.argv)
jarvis = Main()
jarvis.show()
exit(app.exec_())
