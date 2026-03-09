import pyttsx3
import threading

from Jarvis.features import date_time
from Jarvis.features import launch_app
from Jarvis.features import website_open
from Jarvis.features import wikipedia
from Jarvis.features import google_search
from Jarvis.features import note
from Jarvis.features import system_stats
from Jarvis.features import loc
from Jarvis.services import ollama_chat
from Jarvis.features.voice_input import VoiceInputService
from Jarvis.config import config

class JarvisAssistant:
    def __init__(self):
        self.voice_input = VoiceInputService(config)
        self.tts_enabled = getattr(config, 'tts_enabled', True)
        self.tts_rate = getattr(config, 'tts_rate', 175)
        self.tts_voice_index = getattr(config, 'tts_voice_index', 0)
        self._tts_lock = threading.Lock()
        self.engine = None
        self._init_tts_engine()

    @property
    def keyboard_fallback(self):
        return self.voice_input.keyboard_fallback

    @keyboard_fallback.setter
    def keyboard_fallback(self, value):
        self.voice_input.keyboard_fallback = value

    @property
    def voice_runtime_available(self):
        return self.voice_input.voice_runtime_available

    @voice_runtime_available.setter
    def voice_runtime_available(self, value):
        self.voice_input.voice_runtime_available = value

    @property
    def microphone_device_index(self):
        return self.voice_input.microphone_device_index

    def list_microphones_with_diagnostics(self):
        return self.voice_input.list_microphones_with_diagnostics()

    def list_microphones(self):
        return self.voice_input.list_microphones()

    def set_microphone_device(self, device_index):
        return self.voice_input.set_microphone_device(device_index)

    def _init_tts_engine(self):
        try:
            self.engine = pyttsx3.init('sapi5')
            voices = self.engine.getProperty('voices')
            if voices:
                index = max(0, min(self.tts_voice_index, len(voices) - 1))
                self.engine.setProperty('voice', voices[index].id)
            self.engine.setProperty('rate', self.tts_rate)
            return True
        except Exception as e:
            print(f"TTS init error: {e}")
            self.engine = None
            return False

    def mic_input(self):
        return self.voice_input.mic_input()


    def tts(self, text):
        """
        Convert any text to speech
        :param text: text(String)
        :return: True/False (Play sound if True otherwise write exception to log and return  False)
        """
        if not self.tts_enabled:
            return False

        if not text:
            return False

        with self._tts_lock:
            if self.engine is None and not self._init_tts_engine():
                return False

            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except Exception as e:
                print(f"TTS runtime error: {e}")
                self.engine = None
                return False

    def tell_me_date(self):

        return date_time.date()

    def tell_time(self):

        return date_time.time()

    def launch_any_app(self, path_of_app):
        """
        Launch any windows application 
        :param path_of_app: path of exe 
        :return: True is success and open the application, False if fail
        """
        return launch_app.launch_app(path_of_app)

    def website_opener(self, domain):
        """
        This will open website according to domain
        :param domain: any domain, example "youtube.com"
        :return: True if success, False if fail
        """
        return website_open.website_opener(domain)


    def tell_me(self, topic):
        """
        Tells about anything from wikipedia
        :param topic: any string is valid options
        :return: First 500 character from wikipedia if True, False if fail
        """
        return wikipedia.tell_me_about(topic)
    
    def search_anything_google(self, command):
        return google_search.google_search(command)

    def take_note(self, text):
        note.note(text)
    
    def system_info(self):
        return system_stats.system_stats()

    def location(self, location):
        current_loc, target_loc, distance = loc.loc(location)
        return current_loc, target_loc, distance

    def my_location(self):
        city, state, country = loc.my_location()
        return city, state, country

    def ask_ollama(self, prompt):
        return ollama_chat.ask_ollama(
            prompt=prompt,
            model=getattr(config, 'ollama_model', 'llama3.2'),
            base_url=getattr(config, 'ollama_url', 'http://127.0.0.1:11434'),
            system_prompt=getattr(
                config,
                'ollama_system_prompt',
                'You are Jarvis, a concise and helpful local AI assistant.',
            ),
            timeout=getattr(config, 'ollama_timeout', 120),
            num_gpu=getattr(config, 'ollama_num_gpu', -1),
            num_ctx=getattr(config, 'ollama_num_ctx', 8192),
            temperature=getattr(config, 'ollama_temperature', 0.6),
            num_thread=getattr(config, 'ollama_num_thread', 0),
            auto_select_model=getattr(config, 'ollama_auto_select_model', True),
            auto_route_by_prompt=getattr(config, 'ollama_auto_route_by_prompt', True),
            model_candidates=getattr(config, 'ollama_model_candidates', None),
            connect_timeout=getattr(config, 'ollama_connect_timeout', 5),
            model_discovery_timeout=getattr(config, 'ollama_model_discovery_timeout', 5),
        )

    def list_ollama_models(self):
        return ollama_chat.list_available_models(
            base_url=getattr(config, 'ollama_url', 'http://127.0.0.1:11434'),
            timeout=getattr(config, 'ollama_model_discovery_timeout', 5),
        )

    def preview_ollama_model(self, prompt):
        return ollama_chat.preview_routed_model(
            prompt=prompt,
            model=getattr(config, 'ollama_model', 'llama3.2'),
            base_url=getattr(config, 'ollama_url', 'http://127.0.0.1:11434'),
            timeout=getattr(config, 'ollama_timeout', 120),
            auto_select_model=getattr(config, 'ollama_auto_select_model', True),
            auto_route_by_prompt=getattr(config, 'ollama_auto_route_by_prompt', True),
            model_candidates=getattr(config, 'ollama_model_candidates', None),
            connect_timeout=getattr(config, 'ollama_connect_timeout', 5),
            model_discovery_timeout=getattr(config, 'ollama_model_discovery_timeout', 5),
        )