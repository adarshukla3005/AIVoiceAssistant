# AI Voice Assistant

An intelligent **voice-controlled assistant** built using **FastAPI**, **JavaScript**, and **SpeechRecognition**, capable of responding to voice commands and speaking out responses.

---

## Demo Video  

Watch the AI Voice Assistant in action! Click below to see the demo:  

[![Watch the Demo](https://img.shields.io/badge/🎬%20Watch%20Demo-red?style=for-the-badge&logo=youtube&logoColor=white)](https://drive.google.com/file/d/1VO3oB-xlbUoMArAsB-jTZHY_eJ76Fovj/view?usp=sharing)

## Features  
**Trigger with "Alexa" Command** – Starts listening when you say "Alexa"  
**Voice Recognition** – Converts speech to text using **Google SpeechRecognition**  
**Text Command Processing** – Understands basic commands like time, greetings, and weather  
**Speech Response** – Speaks the assistant's response using **pyttsx3**  
**Interactive UI** – Includes a simple, responsive **frontend with animations**  
**Start/Stop Listening** – Control assistant via UI buttons  

---

## Tech Stack  

| Technology  | Purpose |
|-------------|---------|
| **FastAPI** | Backend API |
| **JavaScript** | Handles frontend voice interactions |
| **SpeechRecognition** | Converts voice to text |
| **pyttsx3** | Converts text to speech |
| **HTML + CSS** | User interface |

---

### UI Preview  
![Untitledvideo-MadewithClipchamp-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/baab315e-d0ef-41bf-aafc-04eb4e4263e8)

### How It Works  
1️⃣ Click **"Start Voice Command"**  
2️⃣ Say **"Alexa"** and then give your command  
3️⃣ The assistant **processes your request** and **speaks the response**  
4️⃣ Click **"Stop Assistant"** to **stop the response**  

---

## Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/ai-voice-assistant.git
cd ai-voice-assistant
```

### 2️⃣ Install Dependencies  
Make sure you have **Python 3.7+** installed. Then, run:  

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the FastAPI Server

```
uvicorn main:app --reload
```

Your server will now run at http://127.0.0.1:8000/ 🎉

### 4️⃣ Open the Web Interface
Once the server is running, open index.html in your browser.

## Project Structure  

```csharp
ai-voice-assistant/
│── static/               # Frontend HTML, CSS, JavaScript
│── main.py               # FastAPI backend
│── README.md             # Project documentation
│── requirements.txt      # Dependencies
```


## 🔗API Endpoints
```
Method	Endpoint	         Description
GET	    /voice-command	   Starts listening for "Alexa"
POST	  /text-command	     Processes the command
POST	  /stop-speak	       Stops assistant
```


