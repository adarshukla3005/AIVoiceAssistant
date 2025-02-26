import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pywhatkit
import pyjokes
import requests
import google.generativeai as genai
import os
import webbrowser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv  # Load environment variables
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading
from fastapi.middleware.cors import CORSMiddleware

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Text-to-Speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize the flag for stopping speech
stop_speaking_flag = False

# Email credentials (Replace with your actual email credentials)
EMAIL_ADDRESS = "adarshukla3005@gmail.com"
EMAIL_PASSWORD = "Adarshraj30#"

# Predefined email contacts
contacts = {
    "garvit": "garvit@ph.iitr.ac.in",
    "adarsh": "shukla305adarsh@gmail.com"
}

# Data model for incoming requests
class CommandRequest(BaseModel):
    command: str

# Function to convert text to speech
def talk(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to capture voice command
def take_command():
    listener = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for commands...")
            listener.adjust_for_ambient_noise(source, duration=1)
            listener.pause_threshold = 1.5
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
    prompt = f"You are a smartest AI assistant you understand to every command give great output response. Respond to this query:\n\nUser: {command}\n\nAI:"
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
    elif "email" in command:
        return "send_email"
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
        app = command.replace("open", "").strip()
        os.system(f"start {app}")
        return f"Opening {app}."

    # elif category == "send_email":
    #     return "Sorry, email sending is not fully implemented yet."

    else:
        return ai_response(command)

# Function to start listening for commands automatically
async def listen_for_commands():
    global stop_speaking_flag
    # talk("Hi Adarsh, how can I help you today?")  # Greet when app starts
    while True:
        command = take_command()
        if stop_speaking_flag:
            engine.stop()
            stop_speaking_flag = False
            break
        response = process_command(command)
        talk(response)  # Speak the response

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up template rendering
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def serve_home(request: Request):
    talk("Hi Adarsh, how can I help you today?")
    return templates.TemplateResponse("index.html", {"request": request})

# Route to get the text command and process it
@app.post("/text-command")
async def text_command(request: CommandRequest):
    command = request.command
    response = process_command(command)
    return {"command": command, "response": response}

# Route to process voice commands from frontend
@app.get("/voice-command")
async def voice_command(background_tasks: BackgroundTasks):
    background_tasks.add_task(listen_for_commands)  # Runs in the background
    return {"message": "Listening for command..."}

# Route for speaking the assistant's response
@app.post("/speak")
async def speak_text(data: dict):
    text = data.get("command", "")
    
    def speak():
        local_engine = pyttsx3.init()  # Create a new instance inside the thread
        local_engine.say(text)
        local_engine.runAndWait()

    # Run the function in a separate thread
    thread = threading.Thread(target=speak)
    thread.start()
    return {"message": "Speaking..."}

@app.post("/stop-speak")
async def stop_speak():
    global stop_speaking_flag
    stop_speaking_flag = True
    return {"message": "Speech stopped"}

# Background task to start listening for commands on app start
@app.on_event("startup")
async def on_startup():
    # Start listening for commands continuously in the background
    asyncio.create_task(listen_for_commands())
