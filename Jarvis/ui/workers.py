import time

from PyQt5.QtCore import QThread, pyqtSignal


class OllamaUiWorker(QThread):
    response_ready = pyqtSignal(str, float, str)
    response_error = pyqtSignal(str, float, str)

    def __init__(self, prompt, ask_local_llm, routed_model=""):
        super().__init__()
        self.prompt = prompt
        self.ask_local_llm = ask_local_llm
        self.routed_model = routed_model

    def run(self):
        started_at = time.perf_counter()
        try:
            response = self.ask_local_llm(self.prompt)
            if not response:
                response = "I received an empty response from the model."
            elapsed = time.perf_counter() - started_at
            self.response_ready.emit(response, elapsed, self.routed_model)
        except Exception as error:
            elapsed = time.perf_counter() - started_at
            self.response_error.emit(str(error), elapsed, self.routed_model)


class VoiceInputWorker(QThread):
    command_ready = pyqtSignal(str)
    capture_error = pyqtSignal(str)

    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant

    def run(self):
        original_keyboard_fallback = self.assistant.keyboard_fallback
        try:
            # In UI mode we do not want microphone failures to block on terminal input.
            self.assistant.keyboard_fallback = False
            self.assistant.voice_runtime_available = True
            command = self.assistant.mic_input()
            if not command:
                self.capture_error.emit("No voice input detected.")
                return
            self.command_ready.emit(command)
        except Exception as error:
            self.capture_error.emit(str(error))
        finally:
            self.assistant.keyboard_fallback = original_keyboard_fallback
