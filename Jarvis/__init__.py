import speech_recognition as sr
import pyttsx3
import threading

from Jarvis.features import date_time
from Jarvis.features import launch_app
from Jarvis.features import website_open
from Jarvis.features import weather
from Jarvis.features import wikipedia
from Jarvis.features import news
from Jarvis.features import send_email
from Jarvis.features import google_search
from Jarvis.features import note
from Jarvis.features import system_stats
from Jarvis.features import loc
from Jarvis.features import ollama_chat
from Jarvis.config import config

class JarvisAssistant:
    def __init__(self):
        self.voice_input_enabled = getattr(config, 'voice_input_enabled', True)
        self.voice_retry_limit = getattr(config, 'voice_retry_limit', 2)
        self.keyboard_fallback = getattr(config, 'keyboard_fallback', True)
        self.voice_runtime_available = self.voice_input_enabled
        self.tts_enabled = getattr(config, 'tts_enabled', True)
        self.tts_rate = getattr(config, 'tts_rate', 175)
        self.tts_voice_index = getattr(config, 'tts_voice_index', 0)
        self._tts_lock = threading.Lock()
        self.engine = None
        self._init_tts_engine()

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

    def _text_fallback_input(self, prompt="Type command: "):
        try:
            return input(prompt).strip().lower()
        except Exception:
            return False

    def mic_input(self):
        """
        Fetch input from mic
        return: user's voice input as text if true, false if fail
        """
        if not self.voice_runtime_available:
            return self._text_fallback_input()

        recognizer = sr.Recognizer()
        attempts = 0

        while attempts <= self.voice_retry_limit:
            try:
                with sr.Microphone() as source:
                    print("Listening....")
                    recognizer.energy_threshold = 4000
                    audio = recognizer.listen(source)

                print("Recognizing...")
                command = recognizer.recognize_google(audio, language='en-in').lower()
                print(f'You said: {command}')
                return command
            except Exception as e:
                print(e)
                attempts += 1
                if attempts <= self.voice_retry_limit:
                    print("Voice input failed, retrying...")

        if self.keyboard_fallback:
            print("Voice input unavailable. Falling back to keyboard input.")
            self.voice_runtime_available = False
            return self._text_fallback_input()

        return False


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


    def weather(self, city):
        """
        Return weather
        :param city: Any city of this world
        :return: weather info as string if True, or False
        """
        try:
            res = weather.fetch_weather(city)
        except Exception as e:
            print(e)
            res = False
        return res

    def tell_me(self, topic):
        """
        Tells about anything from wikipedia
        :param topic: any string is valid options
        :return: First 500 character from wikipedia if True, False if fail
        """
        return wikipedia.tell_me_about(topic)

    def news(self):
        """
        Fetch top news of the day from google news
        :return: news list of string if True, False if fail
        """
        return news.get_news()
    
    def send_mail(self, sender_email, sender_password, receiver_email, msg):

        return send_email.mail(sender_email, sender_password, receiver_email, msg)

    def google_calendar_events(self, text):
        try:
            from Jarvis.features import google_calendar
        except Exception as e:
            print(e)
            return False

        service = google_calendar.authenticate_google()
        date = google_calendar.get_date(text) 
        
        if date:
            return google_calendar.get_events(date, service)
        else:
            pass
    
    def search_anything_google(self, command):
        google_search.google_search(command)

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
        )