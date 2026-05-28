import datetime
import webbrowser
import os
import urllib.parse
import subprocess

import requests
import pyautogui
import psutil
import pyttsx3
import speech_recognition as sr

from google import genai
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

print("API KEY:", GEMINI_API_KEY)

# =========================
# GEMINI CLIENT
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# SPEECH RECOGNITION
# =========================

listener = sr.Recognizer()

# =========================
# VOICE ENGINE
# =========================

engine = pyttsx3.init()

engine.setProperty("rate", 170)

# =========================
# SPEAK FUNCTION
# =========================


def speak(text):

    print("Assistant:", text)

    engine.say(text)

    engine.runAndWait()


# =========================
# LISTEN FUNCTION
# =========================

def take_command():

    try:

        with sr.Microphone() as source:

            print("Listening...")

            listener.adjust_for_ambient_noise(source, duration=1)

            audio = listener.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

            command = listener.recognize_google(audio)

            command = command.lower()

            print("You said:", command)

            return command

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        return ""

    except Exception as e:

        print("Error:", e)

        return ""


# =========================
# GEMINI AI FUNCTION
# =========================

def ask_gemini(question):

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=question
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return "Sorry, internet AI is unavailable right now"


# =========================
# WEATHER FUNCTION
# =========================

def get_weather(city="Mumbai"):

    try:

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

        response = requests.get(url)

        data = response.json()

        if data["cod"] != 200:
            return "City not found"

        temp = data["main"]["temp"]

        weather = data["weather"][0]["description"]

        return f"The temperature in {city} is {temp} degree Celsius with {weather}"

    except Exception as e:

        print("Weather Error:", e)

        return "Sorry, I cannot fetch weather right now"


# =========================
# OPEN APPS
# =========================

def open_app(command):

    if "youtube" in command:

        webbrowser.open("https://youtube.com")

        speak("Opening YouTube")

    elif "google" in command:

        webbrowser.open("https://google.com")

        speak("Opening Google")

    elif "spotify" in command:

        webbrowser.open("https://open.spotify.com")

        speak("Opening Spotify")

    elif "whatsapp" in command:

        webbrowser.open("https://web.whatsapp.com")

        speak("Opening WhatsApp")

    elif "notepad" in command:

        os.system("notepad")

        speak("Opening Notepad")

    else:

        speak("Application not found")

# =========================
# CLOSE APPS
# =========================

def close_app(command):

    apps = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "spotify": "chrome.exe",
        "youtube": "chrome.exe",
        "whatsapp": "chrome.exe"
    }

    for app_name, process_name in apps.items():

        if app_name in command:

            found = False

            for process in psutil.process_iter():

                try:

                    if process.name().lower() == process_name.lower():

                        process.kill()

                        found = True

                except:
                    pass

            if found:

                speak(f"Closing {app_name}")

            else:

                speak(f"{app_name} is not running")

            return


# =========================
# PLAY MUSIC
# =========================

def play_music(command):

    song = command.replace("play", "").strip()

    if song == "":
        speak("Please say the song name")
        return

    query = urllib.parse.quote(song)

    url = f"https://open.spotify.com/search/{query}"

    webbrowser.open(url)

    speak(f"Playing {song} on Spotify")


# =========================
# SCREENSHOT FUNCTION
# =========================

def take_screenshot():

    try:

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"screenshot_{now}.png"

        screenshot = pyautogui.screenshot()

        screenshot.save(filename)

        speak("Screenshot taken successfully")

    except Exception as e:

        print("Screenshot Error:", e)

        speak("Unable to take screenshot")


# =========================
# MAIN ASSISTANT FUNCTION
# =========================

def run_assistant():

    command = take_command()

    if command == "":
        return

    # HELLO

    if "hello" in command:

        speak("Hello Kavya")

    # TIME

    elif "time" in command:

        current_time = datetime.datetime.now().strftime("%I:%M %p")

        speak("Current time is " + current_time)

    # DATE

    elif "date" in command:

        today = datetime.datetime.now().strftime("%d %B %Y")

        speak("Today's date is " + today)

    # WEATHER

    elif "weather" in command:

        city = "Mumbai"

        if "in" in command:

            city = command.split("in")[-1].strip()

        weather_report = get_weather(city)

        speak(weather_report)

    # OPEN APPS

    elif "open" in command:

        open_app(command)

    # CLOSE APPS

    elif "close" in command:

        close_app(command)

    # PLAY MUSIC

    elif "play" in command:

        play_music(command)

    # SCREENSHOT

    elif "screenshot" in command:

        take_screenshot()

    # EXIT

    elif "bye" in command or "exit" in command:

        speak("Goodbye Kavya")

        exit()

    # AI CHAT

    else:

        answer = ask_gemini(command)

        speak(answer)


# =========================
# START ASSISTANT
# =========================

speak("AI Assistant Started")

while True:

    run_assistant()