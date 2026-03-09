import re
import webbrowser
import urllib.parse
import pyttsx3



def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voices', voices[0].id)
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 180)


def google_search(command):
    reg_ex = re.search('search google for (.*)', command)
    if not reg_ex:
        speak("Sorry sir, I couldn't understand the Google search query")
        return

    search_for = reg_ex.group(1).strip()
    if not search_for:
        speak("Sorry sir, please tell me what to search for")
        return

    speak("Okay sir!")
    speak(f"Searching for {search_for}")
    query = urllib.parse.quote_plus(search_for)
    webbrowser.open(f"https://www.google.com/search?q={query}")