from Jarvis import JarvisAssistant
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem
from Jarvis.ui.gui import Ui_MainWindow
from Jarvis.ui.workers import OllamaUiWorker, VoiceInputWorker
from Jarvis.services.command_router import CommandRouter
from Jarvis.services.ollama_chat import check_ollama_health
from Jarvis.services.ai_runtime import ask_local_llm as ask_local_llm_service
from Jarvis.services.ai_runtime import computational_intelligence as computational_intelligence_service
from Jarvis.services.program_runtime import startup as startup_service
from Jarvis.config import config

obj = JarvisAssistant()
FORCE_LOCAL_CHAT_MODE = getattr(config, "force_local_chat_mode", True)
ENABLE_VOICE_LOOP_IN_UI = getattr(config, "enable_voice_loop_in_ui", False)
UI_SPEAK_RESPONSES = getattr(config, "ui_speak_responses", False)

# ================================ MEMORY ===========================================================================================================

GREETINGS = ["hello jarvis", "jarvis", "wake up jarvis", "you there jarvis", "time to work jarvis", "hey jarvis",
             "ok jarvis", "are you there"]
GREETINGS_RES = ["always there for you sir", "i am ready sir",
                 "your wish my command", "how can i help you sir?", "i am online and ready sir"]
# =======================================================================================================================================================


def speak(text):
    if text:
        print(f"Jarvis: {text}")
    obj.tts(text)


def ask_local_llm(question):
    return ask_local_llm_service(obj, question)


def computational_intelligence(question):
    return computational_intelligence_service(obj, question)
    
def startup():
    startup_service(
        speak=speak,
        assistant=obj,
        force_local_chat_mode=FORCE_LOCAL_CHAT_MODE,
        enable_voice_loop_in_ui=ENABLE_VOICE_LOOP_IN_UI,
        voice_input_enabled=getattr(config, "voice_input_enabled", True),
    )
    



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
            computational_intelligence=computational_intelligence,
            ask_local_llm=ask_local_llm,
            greetings=GREETINGS,
            greeting_responses=GREETINGS_RES,
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


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Scope background styling to the central widget only so child controls keep their own colors.
        self.ui.centralwidget.setStyleSheet("#centralwidget { background-color: rgb(0, 0, 0); }")
        self.started = False
        self.ui_router = CommandRouter(
            assistant=obj,
            speak=speak,
            config=config,
            computational_intelligence=computational_intelligence,
            ask_local_llm=ask_local_llm,
            greetings=GREETINGS,
            greeting_responses=GREETINGS_RES,
        )
        self.chat_worker = None
        self.voice_worker = None
        self.clock_timer = None
        self.ollama_health_ok = False
        self.model_items = {}
        self.active_model_name = ""
        self.setup_chat_controls()
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton.setText("Running")
        self.ui.pushButton.setEnabled(False)
        QtCore.QTimer.singleShot(0, self.startTask)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_dynamic_layout()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def setup_chat_controls(self):
        # Expand chat viewport for longer responses.
        self.ui.textBrowser_3.setGeometry(QtCore.QRect(450, 120, 980, 650))
        self.ui.textBrowser_3.setStyleSheet(
            "font: 11pt \"MS Shell Dlg 2\";"
            "background-color: rgba(0, 0, 0, 90);"
            "color:white;"
            "border: 1px solid rgba(255, 255, 255, 60);"
            "padding: 8px;"
        )

        self.mic_select_label = QLabel(self.ui.centralwidget)
        self.mic_select_label.setGeometry(QtCore.QRect(20, 120, 90, 28))
        self.mic_select_label.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\"; color: rgb(230, 230, 230);")
        self.mic_select_label.setText("Microphone")

        self.mic_selector = QComboBox(self.ui.centralwidget)
        self.mic_selector.setGeometry(QtCore.QRect(110, 120, 250, 30))
        self.mic_selector.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")

        self.refresh_mic_button = QPushButton(self.ui.centralwidget)
        self.refresh_mic_button.setGeometry(QtCore.QRect(365, 120, 56, 30))
        self.refresh_mic_button.setStyleSheet("background-color: rgb(80, 80, 80);\nfont: 75 9pt \"MS Shell Dlg 2\"; color: white;")
        self.refresh_mic_button.setText("Scan")

        self.status_label = QLabel(self.ui.centralwidget)
        self.status_label.setGeometry(QtCore.QRect(20, 160, 340, 31))
        self.status_label.setStyleSheet("font: 75 11pt \"MS Shell Dlg 2\"; color: rgb(230, 230, 230);")
        self.status_label.setText("Status: Idle")

        self.mic_indicator = QLabel(self.ui.centralwidget)
        self.mic_indicator.setGeometry(QtCore.QRect(365, 165, 20, 20))
        self.mic_indicator.setStyleSheet("background-color: rgb(180, 40, 40); border-radius: 10px;")

        self.mic_label = QLabel(self.ui.centralwidget)
        self.mic_label.setGeometry(QtCore.QRect(390, 162, 56, 24))
        self.mic_label.setStyleSheet("font: 9pt \"MS Shell Dlg 2\"; color: rgb(230, 230, 230);")
        self.mic_label.setText("Mic Off")

        self.voice_button = QPushButton(self.ui.centralwidget)
        self.voice_button.setGeometry(QtCore.QRect(1225, 30, 205, 44))
        self.voice_button.setStyleSheet("background-color: rgb(255, 170, 0);\nfont: 75 11pt \"MS Shell Dlg 2\";")
        self.voice_button.setText("Voice Input")

        self.chat_input = QLineEdit(self.ui.centralwidget)
        self.chat_input.setGeometry(QtCore.QRect(450, 780, 860, 45))
        self.chat_input.setStyleSheet(
            "font: 11pt \"MS Shell Dlg 2\";"
            "color: rgb(255, 255, 255);"
            "background-color: rgba(18, 18, 18, 220);"
            "border: 1px solid rgba(255, 255, 255, 90);"
            "padding-left: 8px;"
        )
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")

        self.send_button = QPushButton(self.ui.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(1320, 780, 110, 45))
        self.send_button.setStyleSheet("background-color: rgb(0, 170, 255);\nfont: 75 12pt \"MS Shell Dlg 2\";")
        self.send_button.setText("Send")

        self.send_button.clicked.connect(self.send_ui_message)
        self.voice_button.clicked.connect(self.capture_voice_input)
        self.refresh_mic_button.clicked.connect(self.populate_microphone_selector)
        self.mic_selector.currentIndexChanged.connect(self.on_microphone_selected)
        self.chat_input.returnPressed.connect(self.send_ui_message)

        self.model_list_label = QLabel(self.ui.centralwidget)
        self.model_list_label.setGeometry(QtCore.QRect(20, 210, 401, 24))
        self.model_list_label.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\"; color: rgb(230, 230, 230);")
        self.model_list_label.setText("Models (green = in use)")

        self.model_list = QListWidget(self.ui.centralwidget)
        self.model_list.setGeometry(QtCore.QRect(20, 235, 401, 430))
        self.model_list.setStyleSheet(
            "QListWidget { background-color: rgb(30, 30, 30); color: rgb(220, 220, 220); "
            "border: 1px solid rgb(90, 90, 90); font: 9pt 'MS Shell Dlg 2'; }"
        )
        self.model_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.ui.textBrowser_3.append("Jarvis UI chat ready. Jarvis starts automatically.")
        self.ui.textBrowser_3.append("Use the Voice Input button to speak one command.")
        self.ui.textBrowser_3.append("Startup check will verify local Ollama connectivity.")
        self.populate_microphone_selector()
        self.populate_model_list()
        self.set_ui_state("Idle")
        self.set_chat_controls_enabled(False)
        self.update_dynamic_layout()

    def update_dynamic_layout(self):
        w = self.ui.centralwidget.width()
        h = self.ui.centralwidget.height()
        margin = 20

        # Always stretch wallpaper to window bounds to avoid white edges on resize.
        self.ui.label.setGeometry(QtCore.QRect(0, 0, w, h))

        left_panel_w = max(320, min(420, int(w * 0.29)))
        left_x = margin
        panel_right = left_x + left_panel_w

        # Keep date/time and voice button aligned at top-right as the window grows.
        top_y = 30
        box_h = 61
        voice_w = 205
        voice_h = 44
        info_w = 220
        gap = 10

        voice_x = max(margin, w - margin - voice_w)
        time_x = max(margin, voice_x - gap - info_w)
        date_x = max(margin, time_x - gap - info_w)

        self.ui.textBrowser.setGeometry(QtCore.QRect(date_x, top_y, info_w, box_h))
        self.ui.textBrowser_2.setGeometry(QtCore.QRect(time_x, top_y, info_w, box_h))
        self.voice_button.setGeometry(QtCore.QRect(voice_x, top_y + 8, voice_w, voice_h))

        # Left utility panel.
        self.mic_select_label.setGeometry(QtCore.QRect(left_x, 120, 90, 28))
        self.mic_selector.setGeometry(QtCore.QRect(left_x + 90, 120, left_panel_w - 150, 30))
        self.refresh_mic_button.setGeometry(QtCore.QRect(panel_right - 56, 120, 56, 30))

        self.status_label.setGeometry(QtCore.QRect(left_x, 160, left_panel_w - 70, 31))
        self.mic_indicator.setGeometry(QtCore.QRect(panel_right - 55, 165, 20, 20))
        self.mic_label.setGeometry(QtCore.QRect(panel_right - 30, 162, 56, 24))

        self.model_list_label.setGeometry(QtCore.QRect(left_x, 210, left_panel_w, 24))
        model_list_h = max(200, h - 290)
        self.model_list.setGeometry(QtCore.QRect(left_x, 235, left_panel_w, model_list_h))

        # Chat area grows with window size.
        chat_x = panel_right + 20
        chat_y = 120
        chat_w = max(360, w - chat_x - margin)
        chat_h = max(220, h - chat_y - 130)
        self.ui.textBrowser_3.setGeometry(QtCore.QRect(chat_x, chat_y, chat_w, chat_h))

        input_y = chat_y + chat_h + 10
        send_w = 110
        self.chat_input.setGeometry(QtCore.QRect(chat_x, input_y, max(220, chat_w - send_w - 10), 45))
        self.send_button.setGeometry(QtCore.QRect(chat_x + chat_w - send_w, input_y, send_w, 45))

        # Keep run/exit controls docked to bottom-right.
        self.ui.pushButton.setGeometry(QtCore.QRect(w - 260, h - 70, 101, 51))
        self.ui.pushButton_2.setGeometry(QtCore.QRect(w - 130, h - 70, 101, 51))

    def populate_model_list(self):
        self.model_items = {}
        self.model_list.clear()
        try:
            models = obj.list_ollama_models()
        except Exception as error:
            models = []
            self.append_ui_chat("System", f"Model list load failed: {error}")

        if not models:
            item = QListWidgetItem("No local models detected")
            self.model_list.addItem(item)
            return

        for name in models:
            item = QListWidgetItem(name)
            self.model_list.addItem(item)
            self.model_items[name.lower()] = item

        if self.active_model_name:
            self.highlight_active_model(self.active_model_name, generating=False)

    def highlight_active_model(self, model_name, generating=True):
        if not model_name:
            return

        self.active_model_name = model_name
        for item in self.model_items.values():
            item.setBackground(QtGui.QColor(30, 30, 30))
            item.setForeground(QtGui.QColor(220, 220, 220))

        active_item = self.model_items.get(model_name.lower())
        if not active_item:
            self.populate_model_list()
            active_item = self.model_items.get(model_name.lower())

        if active_item:
            if generating:
                active_item.setBackground(QtGui.QColor(28, 120, 56))
                active_item.setForeground(QtGui.QColor(255, 255, 255))
            else:
                active_item.setBackground(QtGui.QColor(36, 80, 44))
                active_item.setForeground(QtGui.QColor(230, 255, 230))
            self.model_list.scrollToItem(active_item)

    def check_ollama_startup_health(self):
        base_url = getattr(config, "ollama_url", "http://127.0.0.1:11434")
        ok, message = check_ollama_health(base_url=base_url, timeout=2.5)
        self.ollama_health_ok = ok
        self.append_ui_chat("System", message)
        if ok:
            self.set_ui_state("Idle", "Ollama connected")
            return
        self.set_ui_state("Error", "Ollama unavailable")
        self.append_ui_chat("System", "Model queries may fail until Ollama is reachable.")

    def append_ui_chat(self, speaker, message):
        self.ui.textBrowser_3.append(f"{speaker}: {message}")

    def set_chat_controls_enabled(self, enabled):
        self.chat_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.voice_button.setEnabled(enabled)
        self.mic_selector.setEnabled(enabled)
        self.refresh_mic_button.setEnabled(enabled)

    def populate_microphone_selector(self):
        microphones, diagnostics = obj.list_microphones_with_diagnostics()

        self.mic_selector.blockSignals(True)
        self.mic_selector.clear()

        self.mic_selector.addItem("System default", None)
        for device_index, device_name in microphones:
            self.mic_selector.addItem(f"{device_index}: {device_name}", device_index)

        target_device = obj.microphone_device_index
        selected_index = 0
        if target_device is not None:
            for combo_index in range(self.mic_selector.count()):
                if self.mic_selector.itemData(combo_index) == target_device:
                    selected_index = combo_index
                    break

        self.mic_selector.setCurrentIndex(selected_index)
        self.mic_selector.blockSignals(False)

        if microphones:
            self.append_ui_chat("System", f"Microphone list updated: {len(microphones)} input devices found.")
        else:
            self.append_ui_chat("System", "No microphone input devices found.")
            backend = diagnostics.get("backend") or "unknown"
            self.append_ui_chat("System", f"Mic scan backend: {backend}")
            for error in diagnostics.get("errors", []):
                self.append_ui_chat("System", f"Mic scan detail: {error}")
            self.set_ui_state("Error", "Microphone scan failed")

    def on_microphone_selected(self, combo_index):
        device_index = self.mic_selector.itemData(combo_index)
        if obj.set_microphone_device(device_index):
            selected_name = self.mic_selector.currentText()
            self.append_ui_chat("System", f"Selected microphone: {selected_name}")
            self.set_ui_state("Idle", "Microphone updated")
            return

        self.append_ui_chat("System", "Could not set that microphone device.")
        self.set_ui_state("Error", "Invalid microphone device")

    def set_ui_state(self, state, detail=""):
        detail_text = f" - {detail}" if detail else ""
        self.status_label.setText(f"Status: {state}{detail_text}")

        if state == "Listening":
            self.mic_indicator.setStyleSheet("background-color: rgb(0, 200, 120); border-radius: 10px;")
            self.mic_label.setText("Mic On")
            return

        if state in {"Thinking", "Executing"}:
            self.mic_indicator.setStyleSheet("background-color: rgb(255, 170, 0); border-radius: 10px;")
            self.mic_label.setText("Working")
            return

        if state == "Error":
            self.mic_indicator.setStyleSheet("background-color: rgb(220, 50, 50); border-radius: 10px;")
            self.mic_label.setText("Error")
            return

        self.mic_indicator.setStyleSheet("background-color: rgb(180, 40, 40); border-radius: 10px;")
        self.mic_label.setText("Mic Off")

    def execute_ui_prompt(self, prompt, source_label="You"):
        self.append_ui_chat(source_label, prompt)
        print(f"[UI] User prompt: {prompt}")

        normalized = prompt.lower().strip()
        if normalized in {"goodbye", "offline", "bye", "exit", "quit"}:
            self.append_ui_chat("Jarvis", "Goodbye sir.")
            self.close()
            return

        self.set_ui_state("Executing", "Running local command")
        handled = self.ui_router.route(normalized)
        if handled:
            self.append_ui_chat("Jarvis", f"Task completed: {normalized}")
            self.chat_input.setPlaceholderText("Type a message to Jarvis...")
            self.set_chat_controls_enabled(True)
            self.set_ui_state("Idle")
            self.chat_input.setFocus()
            return

        self.chat_input.setPlaceholderText("Jarvis is thinking...")
        self.set_chat_controls_enabled(False)
        routed_model = ""
        try:
            routed_model = obj.preview_ollama_model(prompt)
        except Exception:
            routed_model = ""

        if routed_model:
            self.highlight_active_model(routed_model, generating=True)
            self.set_ui_state("Thinking", f"Using {routed_model}")
        else:
            self.set_ui_state("Thinking", "Querying local model")

        self.chat_worker = OllamaUiWorker(prompt, ask_local_llm=ask_local_llm, routed_model=routed_model)
        self.chat_worker.response_ready.connect(self.on_ui_response)
        self.chat_worker.response_error.connect(self.on_ui_error)
        self.chat_worker.start()

    def send_ui_message(self):
        if not self.started:
            self.append_ui_chat("System", "Jarvis is still initializing. Please wait a moment.")
            return

        if self.chat_worker and self.chat_worker.isRunning():
            return

        prompt = self.chat_input.text().strip()
        if not prompt:
            return

        self.chat_input.clear()
        self.execute_ui_prompt(prompt, source_label="You")

    def capture_voice_input(self):
        if not self.started:
            self.append_ui_chat("System", "Jarvis is still initializing. Please wait a moment.")
            return

        if self.voice_worker and self.voice_worker.isRunning():
            return

        if self.chat_worker and self.chat_worker.isRunning():
            self.append_ui_chat("System", "Jarvis is still processing your previous message.")
            return

        self.set_chat_controls_enabled(False)
        self.set_ui_state("Listening", "Speak now")
        self.chat_input.setPlaceholderText("Listening to microphone...")

        self.voice_worker = VoiceInputWorker(assistant=obj)
        self.voice_worker.command_ready.connect(self.on_voice_command_ready)
        self.voice_worker.capture_error.connect(self.on_voice_capture_error)
        self.voice_worker.start()

    def on_voice_command_ready(self, command):
        self.execute_ui_prompt(command, source_label="You (voice)")

    def on_voice_capture_error(self, error):
        self.append_ui_chat("System", f"Voice input failed: {error}")
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")
        self.set_chat_controls_enabled(True)
        self.set_ui_state("Error", "Voice capture failed")
        self.chat_input.setFocus()

    def on_ui_response(self, response, elapsed, routed_model):
        self.append_ui_chat("Jarvis", response)
        if routed_model:
            self.append_ui_chat("System", f"Model used: {routed_model}")
            self.highlight_active_model(routed_model, generating=False)
        self.append_ui_chat("System", f"Model latency: {elapsed:.1f}s")
        print(f"[UI] Jarvis response received in {elapsed:.2f}s")
        if UI_SPEAK_RESPONSES:
            speak(response)
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")
        self.set_chat_controls_enabled(True)
        self.set_ui_state("Idle")
        self.chat_input.setFocus()

    def on_ui_error(self, error, elapsed, routed_model):
        msg = f"Could not reach local Ollama: {error}"
        self.append_ui_chat("Jarvis", msg)
        if routed_model:
            self.append_ui_chat("System", f"Attempted model: {routed_model}")
            self.highlight_active_model(routed_model, generating=False)
        self.append_ui_chat("System", f"Request failed after {elapsed:.1f}s")
        print(f"[UI] Error after {elapsed:.2f}s: {error}")
        self.chat_input.setPlaceholderText("Type a message to Jarvis...")
        self.set_chat_controls_enabled(True)
        self.set_ui_state("Error", "Model request failed")
        self.chat_input.setFocus()

    # def run(self):
    #     self.TaskExection
    def startTask(self):
        if self.started:
            return

        self.started = True
        self.ui.movie = QtGui.QMovie("Jarvis/ui/images/live_wallpaper.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QtGui.QMovie("Jarvis/ui/images/initiating.gif")
        self.ui.label_2.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.showTime)
        self.clock_timer.start(1000)
        self.set_chat_controls_enabled(True)
        self.set_ui_state("Idle", "Ready")
        self.chat_input.setFocus()
        self.check_ollama_startup_health()
        self.populate_model_list()

        configured_model = getattr(config, "ollama_model", "")
        if configured_model.startswith("llama4"):
            self.append_ui_chat(
                "System",
                "Performance note: llama4 models are large and can be slow for short prompts on local hardware.",
            )

        if ENABLE_VOICE_LOOP_IN_UI:
            if not startExecution.isRunning():
                print("[UI] Starting voice command loop")
                startExecution.start()
                self.append_ui_chat("System", "Continuous voice loop is enabled in config.")
        else:
            print("[UI] Voice loop disabled; using UI text chat")
            self.append_ui_chat("System", "Voice loop disabled. Use chat or the Voice Input button.")

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
