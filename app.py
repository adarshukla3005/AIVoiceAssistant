import asyncio
import threading
from fastapi import FastAPI
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pywhatkit
import pyjokes
import os
import webbrowser
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import threading
from fastapi.responses import FileResponse
import re


# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Text-to-Speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Global flag for stopping the assistant
stop_speaking_flag = False
assistant_running = False  # Prevents multiple assistant loops

# Data model for text commands
class CommandRequest(BaseModel):
    command: str

# Function to convert text to speech
def talk(text):
    global stop_speaking_flag
    text = re.sub(r"[*]", "", text)  # Remove '*' from the text
    print(f"Assistant: {text}")
    if not stop_speaking_flag:
        engine.say(text)
        engine.runAndWait()

# Function to capture voice command
def take_command():
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for commands...")
            listener.adjust_for_ambient_noise(source, duration=1)
            voice = listener.listen(source, phrase_time_limit=None)
            command = listener.recognize_google(voice).lower()
            print(f"Recognized: {command}")
            return command.strip()
    except sr.UnknownValueError:
        return "I couldn't understand that."
    except sr.RequestError:
        return "Speech recognition service is unavailable."

# Function to get AI response using Google Gemini AI
def ai_response(command):
    prompt = f"You are a smart AI assistant. Respond to this query:\n\nUser: {command}\n\nAI:"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini API Error:", e)
        return "I'm sorry, I couldn't process that request."

# Command categorization
def categorize_command(command):
    if "play" in command:
        return "play_song"
    elif "time" in command:
        return "check_time"
    elif "who is" in command or "what is" in command:
        return "wikipedia", "search_google"
    elif "search for" in command:
        return "search_google"
    elif "joke" in command:
        return "tell_joke"
    elif "open" in command:
        return "open_app"
    else:
        return "general_question"

# Function to execute commands
def process_command(command):

    category = categorize_command(command)

    if category == "play_song":
        song = command.replace("play", "").strip()
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube."

    elif category == "check_time":
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

    elif category == "wikipedia":
        try:
            topic = command.replace("who is", "").replace("what is", "").strip()
            return wikipedia.summary(topic, 1)
        except wikipedia.exceptions.DisambiguationError:
            return "Multiple results found, please be more specific."
        except wikipedia.exceptions.PageError:
            return "I couldn't find any information on that."

    elif category == "search_google":
        query = command.replace("search for", "").strip()
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Here are the search results for {query}."

    elif category == "tell_joke":
        return pyjokes.get_joke()

    elif category == "open_app":
        app_name = command.replace("open", "").strip()
        os.system(f"start {app_name}")
        return f"Opening {app_name}."
    elif command == "":
        return ""
    else:
        return ai_response(command)
    
async def listen_for_commands():
    global stop_speaking_flag
    # while True:
    command = take_command()
    print("-----")
    # if stop_speaking_flag:
    #     engine.stop()
    #     stop_speaking_flag = False
    #     break
    response = process_command(command)
    print("-----")
    talk(response)  # Speak the response
    print("-----")

# Mount static files like CSS, JS, images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template rendering
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def serve_home():
    return FileResponse("templates/index.html")

# Route to process text commands
@app.post("/text-command")
async def text_command(request: CommandRequest):
    command = request.command
    response = process_command(command)
    return {"command": command, "response": response}

# Route to start voice command processing
@app.get("/voice-command")
async def voice_command():
    command = take_command()
    if not command:
        return {"message": "No command detected."}

    response = process_command(command)
    talk(response)  # Speak the response
    
    return {"command": command, "response": response}

# Route to stop voice assistant
@app.post("/stop-speak")
async def stop_listening():
    """Stops voice recognition."""
    global listening, stop_speaking_flag
    listening = False
    stop_speaking_flag = True
    engine.stop()
    return {"message": "Listening stopped"}


# # Start the assistant automatically on server startup
@app.get("/start-assistant")
async def on_startup():
    # global assistant_running
    # if not assistant_running:
    #     assistant_running = True  # Prevent multiple loops
    #     threading.Thread(target=lambda: asyncio.run(listen_for_commands()), daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(listen_for_commands()), daemon=True).start()