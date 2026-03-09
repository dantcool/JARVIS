import os
import random
import re
import time
import datetime
import webbrowser
from urllib.parse import quote

import pyautogui
import pyjokes
import pywhatkit
import requests
from PIL import Image


class CommandRouter:
    def __init__(
        self,
        assistant,
        speak,
        config,
        computational_intelligence,
        ask_local_llm,
        greetings,
        greeting_responses,
    ):
        self.assistant = assistant
        self.speak = speak
        self.config = config
        self.computational_intelligence = computational_intelligence
        self.ask_local_llm = ask_local_llm
        self.greetings = greetings
        self.greeting_responses = greeting_responses
        self.last_screenshot_name = None

        self.handlers = [
            (lambda c: re.search('date', c), self.handle_date),
            (lambda c: "time" in c, self.handle_time),
            (lambda c: c in self.greetings, self.handle_greeting),
            (lambda c: "obsidian" in c and ("open" in c or "review" in c or "show" in c), self.handle_obsidian_review),
            (lambda c: "obsidian" in c and ("note" in c or "remember" in c or "learn" in c), self.handle_obsidian_note),
            (lambda c: re.search('launch', c), self.handle_launch),
            (lambda c: re.search('open|go to|visit', c), self.handle_open),
            (lambda c: re.search('tell me about', c), self.handle_wiki),
            (
                lambda c: c.startswith("search google for ")
                or c.startswith("search web for ")
                or c.startswith("web search for ")
                or c.startswith("search for ")
                or c.startswith("google "),
                self.handle_google_search,
            ),
            (lambda c: "play music" in c or "hit some music" in c, self.handle_play_music),
            (lambda c: 'youtube' in c, self.handle_youtube),
            (lambda c: "calculate" in c or "what is" in c or "who is" in c, self.handle_computation),
            (lambda c: "ask jarvis" in c or c == "jarvis", self.handle_ask_jarvis),
            (lambda c: "make a note" in c or "write this down" in c or "remember this" in c, self.handle_note),
            (lambda c: "close the note" in c or "close notepad" in c, self.handle_close_note),
            (lambda c: "joke" in c, self.handle_joke),
            (lambda c: "system" in c, self.handle_system),
            (lambda c: "where is" in c, self.handle_where_is),
            (lambda c: "ip address" in c, self.handle_ip),
            (lambda c: "switch the window" in c or "switch window" in c, self.handle_switch_window),
            (lambda c: "where i am" in c or "current location" in c or "where am i" in c, self.handle_current_location),
            (lambda c: "take screenshot" in c or "take a screenshot" in c or "capture the screen" in c, self.handle_take_screenshot),
            (lambda c: "show me the screenshot" in c, self.handle_show_screenshot),
            (lambda c: "hide all files" in c or "hide this folder" in c, self.handle_hide_files),
            (lambda c: "visible" in c or "make files visible" in c, self.handle_show_files),
        ]

    def route(self, command):
        for matcher, handler in self.handlers:
            try:
                if matcher(command):
                    handler(command)
                    return True
            except Exception as error:
                self.speak(f"Sorry sir, I hit an error while running that command: {error}")
                return True
        return False

    def handle_date(self, command):
        date_value = self.assistant.tell_me_date()
        print(date_value)
        self.speak(date_value)

    def handle_time(self, command):
        time_value = self.assistant.tell_time()
        print(time_value)
        self.speak(f"Sir the time is {time_value}")

    def handle_greeting(self, command):
        self.speak(random.choice(self.greeting_responses))

    def _obsidian_vault_path(self):
        configured_path = getattr(self.config, "obsidian_vault_path", "")
        if not configured_path:
            return ""
        return os.path.abspath(os.path.expanduser(configured_path))

    def _obsidian_note_relpath(self):
        notes_folder = getattr(self.config, "obsidian_notes_folder", "Jarvis")
        note_name = getattr(self.config, "obsidian_memory_note", "Jarvis Learning Memory.md")
        return os.path.join(notes_folder, note_name)

    def _obsidian_note_abspath(self):
        vault_path = self._obsidian_vault_path()
        if not vault_path:
            return "", ""
        note_relpath = self._obsidian_note_relpath()
        note_abspath = os.path.join(vault_path, note_relpath)
        return vault_path, note_abspath

    def _local_learning_note_path(self):
        configured_path = getattr(self.config, "local_learning_note_path", "")
        if configured_path:
            return os.path.abspath(os.path.expanduser(configured_path))
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "learning_memory.md",
            )
        )

    def _ensure_obsidian_note_exists(self):
        vault_path, note_path = self._obsidian_note_abspath()
        if not vault_path:
            local_note = self._local_learning_note_path()
            os.makedirs(os.path.dirname(local_note), exist_ok=True)
            if not os.path.exists(local_note):
                with open(local_note, "w", encoding="utf-8") as file:
                    file.write("# Jarvis Learning Memory\n\n")
            return "", local_note, ""

        os.makedirs(os.path.dirname(note_path), exist_ok=True)
        if not os.path.exists(note_path):
            with open(note_path, "w", encoding="utf-8") as file:
                file.write("# Jarvis Learning Memory\n\n")
        return vault_path, note_path, ""

    def _open_obsidian_note(self, vault_path, note_path):
        if not vault_path:
            os.startfile(note_path)
            return

        vault_name = os.path.basename(vault_path.rstrip("\\/"))
        note_relpath = os.path.relpath(note_path, vault_path).replace("\\", "/")
        uri = f"obsidian://open?vault={quote(vault_name)}&file={quote(note_relpath)}"
        opened = webbrowser.open(uri)
        if not opened:
            os.startfile(note_path)

    def handle_obsidian_note(self, command):
        if not getattr(self.config, "obsidian_enabled", True):
            self.speak("Obsidian integration is disabled. Saving to local learning memory instead.")

        vault_path, note_path, error = self._ensure_obsidian_note_exists()
        if error:
            self.speak(error)
            return

        triggers = [
            "obsidian note",
            "note in obsidian",
            "save to obsidian",
            "remember in obsidian",
            "learn in obsidian",
        ]
        note_text = command
        for trigger in triggers:
            if trigger in note_text:
                note_text = note_text.replace(trigger, "").strip(" :,-")

        if not note_text:
            self.speak("What should I store in your Obsidian learning notes?")
            note_text = self.assistant.mic_input()

        if not note_text:
            self.speak("I couldn't capture the note text.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(note_path, "a", encoding="utf-8") as file:
            file.write(f"- [{timestamp}] {note_text.strip()}\n")

        if vault_path:
            self.speak("Saved to your Obsidian learning notes.")
        else:
            self.speak("Saved to local learning memory. Obsidian is optional, but recommended as your notes grow.")

        if getattr(self.config, "obsidian_open_after_write", True):
            self._open_obsidian_note(vault_path, note_path)

    def handle_obsidian_review(self, command):
        if not getattr(self.config, "obsidian_enabled", True):
            self.speak("Obsidian integration is disabled. Opening local learning memory.")

        vault_path, note_path, error = self._ensure_obsidian_note_exists()
        if error:
            self.speak(error)
            return

        self._open_obsidian_note(vault_path, note_path)
        if vault_path:
            self.speak("Opening your Obsidian learning notes for review.")
        else:
            self.speak("Opening local learning memory for review.")

    def handle_launch(self, command):
        known_apps = {
            'chrome': 'C:/Program Files/Google/Chrome/Application/chrome'
        }
        parts = command.split(' ', 1)
        if len(parts) < 2:
            self.speak('Please tell me which app to launch')
            return
        app = parts[1].strip()
        path = known_apps.get(app)
        if path is None:
            self.speak('Application path not found')
            print('Application path not found')
        else:
            self.speak('Launching: ' + app + ' for you sir!')
            self.assistant.launch_any_app(path_of_app=path)

    def handle_open(self, command):
        cleaned = command.lower().strip()
        for phrase in ["open", "go to", "visit"]:
            if cleaned.startswith(phrase + " "):
                cleaned = cleaned[len(phrase):].strip()
                break

        domain = cleaned.strip().split(' ')[0] if cleaned else ""
        if not domain:
            self.speak("Please tell me which website to open")
            return

        open_result = self.assistant.website_opener(domain)
        if open_result:
            self.speak(f'Alright sir !! Opening {domain}')
        else:
            self.speak("Sorry sir, I couldn't open that website")
        print(open_result)

    def handle_wiki(self, command):
        topic = command.split(' ')[-1]
        if topic:
            wiki_res = self.assistant.tell_me(topic)
            print(wiki_res)
            self.speak(wiki_res)
            return
        self.speak("Sorry sir. I couldn't load your query from my database. Please try again")

    def handle_google_search(self, command):
        opened, query = self.assistant.search_anything_google(command)
        if not query:
            self.speak("Please tell me what to search for on the web")
            return
        if opened:
            self.speak(f"Searching the web for {query}")
            return
        self.speak("I prepared your search, but I could not open the browser")

    def handle_play_music(self, command):
        music_dir = "F://Songs//Imagine_Dragons"
        songs = os.listdir(music_dir)
        for song in songs:
            os.startfile(os.path.join(music_dir, song))

    def handle_youtube(self, command):
        parts = command.split(' ')
        if len(parts) < 2:
            self.speak("Please tell me what to play on youtube")
            return
        video = parts[1]
        self.speak(f"Okay sir, playing {video} on youtube")
        pywhatkit.playonyt(video)

    def handle_computation(self, command):
        answer = self.computational_intelligence(command)
        self.speak(answer)

    def handle_ask_jarvis(self, command):
        prompt = command.replace("ask jarvis", "", 1).strip()
        if prompt == "jarvis" or not prompt:
            self.speak("What would you like to ask?")
            prompt = self.assistant.mic_input()
        answer = self.ask_local_llm(prompt)
        self.speak(answer)

    def handle_note(self, command):
        self.speak("What would you like me to write down?")
        note_text = self.assistant.mic_input()
        self.assistant.take_note(note_text)
        self.speak("I've made a note of that")

    def handle_close_note(self, command):
        self.speak("Okay sir, closing notepad")
        os.system("taskkill /f /im notepad++.exe")

    def handle_joke(self, command):
        joke = pyjokes.get_joke()
        print(joke)
        self.speak(joke)

    def handle_system(self, command):
        sys_info = self.assistant.system_info()
        print(sys_info)
        self.speak(sys_info)

    def handle_where_is(self, command):
        place = command.split('where is ', 1)[1]
        current_loc, target_loc, distance = self.assistant.location(place)
        city = target_loc.get('city', '')
        state = target_loc.get('state', '')
        country = target_loc.get('country', '')
        time.sleep(1)
        try:
            if city:
                res = f"{place} is in {state} state and country {country}. It is {distance} km away from your current location"
                print(res)
                self.speak(res)
            else:
                res = f"{state} is a state in {country}. It is {distance} km away from your current location"
                print(res)
                self.speak(res)
        except Exception:
            res = "Sorry sir, I couldn't get the co-ordinates of the location you requested. Please try again"
            self.speak(res)

    def handle_ip(self, command):
        ip = requests.get('https://api.ipify.org').text
        print(ip)
        self.speak(f"Your ip address is {ip}")

    def handle_switch_window(self, command):
        self.speak("Okay sir, Switching the window")
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
        time.sleep(1)
        pyautogui.keyUp("alt")

    def handle_current_location(self, command):
        try:
            city, state, country = self.assistant.my_location()
            print(city, state, country)
            self.speak(f"You are currently in {city} city which is in {state} state and country {country}")
        except Exception:
            self.speak("Sorry sir, I coundn't fetch your current location. Please try again")

    def handle_take_screenshot(self, command):
        self.speak("By what name do you want to save the screenshot?")
        name = self.assistant.mic_input()
        if not name:
            self.speak("Sorry sir, I could not catch the screenshot name")
            return
        self.speak("Alright sir, taking the screenshot")
        img = pyautogui.screenshot()
        self.last_screenshot_name = f"{name}.png"
        img.save(self.last_screenshot_name)
        self.speak("The screenshot has been succesfully captured")

    def handle_show_screenshot(self, command):
        try:
            if not self.last_screenshot_name:
                self.speak("No screenshot has been captured yet")
                return
            img = Image.open(self.last_screenshot_name)
            img.show(img)
            self.speak("Here it is sir")
            time.sleep(2)
        except IOError:
            self.speak("Sorry sir, I am unable to display the screenshot")

    def handle_hide_files(self, command):
        os.system("attrib +h /s /d")
        self.speak("Sir, all the files in this folder are now hidden")

    def handle_show_files(self, command):
        os.system("attrib -h /s /d")
        self.speak("Sir, all the files in this folder are now visible to everyone. I hope you are taking this decision in your own peace")
