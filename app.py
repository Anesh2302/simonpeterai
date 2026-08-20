import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

SYSTEM_PROMPT = """You are SimonPeter AI, a helpful personal assistant created by Anesh G J. You are knowledgeable, friendly, and can help with:
- General knowledge questions (science, history, geography, math, etc.)
- Programming help (Python, JavaScript, HTML/CSS, etc.)
- cybersecurity questions
- Weather information
- Calculations and math
- General advice and conversation
- Tech recommendations
- Current events and general knowledge

Be concise, helpful, and conversational. If you don't know something, say so honestly. You can use markdown formatting in your responses."""


def call_nvidia_ai(message, history=None):
    if not NVIDIA_API_KEY:
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for h in history[-10:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})

    try:
        resp = requests.post(
            NVIDIA_URL,
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": NVIDIA_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


def smart_fallback(message):
    lower = message.lower().strip()

    if any(w in lower for w in ["who are you", "what are you", "your name"]):
        return "I'm **SimonPeter AI**, a personal assistant created by **Anesh G J**. I can help with questions about science, math, programming, cybersecurity, and much more. I'm powered by AI when available, and have built-in knowledge for many topics. How can I help you today?"

    if any(w in lower for w in ["who made you", "who created you", "your creator"]):
        return "I was created by **Anesh G J**, a cybersecurity-focused full-stack developer. He built me as part of his portfolio to demonstrate AI integration and full-stack development skills."

    greetings = ["hi", "hello", "hey", "sup", "yo", "hola", "good morning", "good evening", "good afternoon"]
    if any(lower.startswith(g) for g in greetings):
        return "Hey there! I'm SimonPeter AI. I can help you with questions on any topic, math calculations, programming, cybersecurity, and general knowledge. What would you like to know?"

    if any(w in lower for w in ["thank", "thanks", "thx"]):
        return "You're welcome! Is there anything else I can help you with?"

    if any(w in lower for w in ["bye", "goodbye", "see you"]):
        return "Goodbye! Feel free to come back anytime you need help."

    if any(w in lower for w in ["help", "what can you do", "features"]):
        return """I can help you with many things:

**Knowledge & Education**
- Science, history, geography, math
- Technology and programming
- Cybersecurity concepts

**Practical Tools**
- Math calculations
- Web searches (via the Search tab)
- Weather updates (via the Weather tab)

**Conversation**
- General advice and discussion
- Tech recommendations
- Career guidance

Just ask me anything! I'll do my best to give you a helpful and accurate answer."""

    if any(w in lower for w in ["python", "programming", "code", "javascript", "html", "css"]):
        if "python" in lower:
            return "**Python** is a versatile programming language. Here are some key concepts:\n\n- **Syntax**: Clean and readable, uses indentation\n- **Data Types**: int, float, str, list, dict, tuple, set\n- **Libraries**: Flask (web), NumPy (math), Pandas (data), TensorFlow (AI)\n- **Example**: `print('Hello, World!')`\n\nWhat specific Python topic would you like to learn about?"
        elif "javascript" in lower:
            return "**JavaScript** is the language of the web. Key concepts:\n\n- **ES6+**: Arrow functions, template literals, destructuring\n- **Frameworks**: React, Vue, Angular\n- **Node.js**: Server-side JavaScript\n- **Example**: `console.log('Hello, World!')`\n\nWhat JavaScript topic interests you?"
        return "Programming is a great skill! I can help with **Python**, **JavaScript**, **HTML/CSS**, **Java**, **C/C++**, and more. What language or concept would you like to explore?"

    if any(w in lower for w in ["cyber", "security", "hack", "vulnerability", "penetration"]):
        return "**Cybersecurity** is a critical field. Key areas:\n\n- **Network Security**: Firewalls, IDS/IPS, VPNs\n- **Web Security**: XSS, SQL injection, CSRF prevention\n- **Cryptography**: AES, RSA, hashing (SHA-256), SSL/TLS\n- **Penetration Testing**: Reconnaissance, scanning, exploitation\n- **Defense**: Incident response, forensics, hardening\n\nAnesh G J (my creator) specializes in this field. What aspect interests you?"

    if any(w in lower for w in ["math", "calculate", "compute", "equation"]):
        import re
        nums = re.findall(r'[\d.]+', lower)
        if "square" in lower and nums:
            n = float(nums[0])
            return f"The square of **{n}** is **{n**2}**."
        if "sqrt" in lower and nums:
            import math
            n = float(nums[0])
            return f"The square root of **{n}** is **{math.sqrt(n):.4f}**."
        if any(op in lower for op in ["+", "plus", "add"]):
            if len(nums) >= 2:
                return f"**{nums[0]} + {nums[1]} = {float(nums[0]) + float(nums[1])}**"
        if any(op in lower for op in ["-", "minus", "subtract"]):
            if len(nums) >= 2:
                return f"**{nums[0]} - {nums[1]} = {float(nums[0]) - float(nums[1])}**"
        if any(op in lower for op in ["*", "times", "multiply"]):
            if len(nums) >= 2:
                return f"**{nums[0]} × {nums[1]} = {float(nums[0]) * float(nums[1])}**"
        if any(op in lower for op in ["/", "divide", "divided"]):
            if len(nums) >= 2 and float(nums[1]) != 0:
                return f"**{nums[0]} ÷ {nums[1]} = {float(nums[0]) / float(nums[1]):.4f}**"
        return "I can help with math! Try something like:\n- 'What is 25 + 37?'\n- 'Calculate 144 square root'\n- 'What is 15 times 8?'"

    if any(w in lower for w in ["time", "what time", "current time"]):
        from datetime import datetime
        now = datetime.now()
        return f"The current time is **{now.strftime('%I:%M %p')}** on **{now.strftime('%A, %B %d, %Y')}**."

    if any(w in lower for w in ["date", "today", "what day"]):
        from datetime import datetime
        now = datetime.now()
        return f"Today is **{now.strftime('%A, %B %d, %Y')}**."

    if any(w in lower for w in ["joke", "funny", "laugh"]):
        import random
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache!",
            "What's a programmer's favorite hangout place? Foo Bar!",
            "Why do Java developers wear glasses? Because they can't C#!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why was the computer cold? It left its Windows open!",
            "What do you call a computer that sings? A-Dell!",
        ]
        return random.choice(jokes)

    if any(w in lower for w in ["weather", "temperature", "forecast"]):
        return "I can check the weather! Please use the **Weather tab** in the sidebar and enter your city name. I'll fetch real-time weather data for you."

    if any(w in lower for w in ["note", "remember", "write down"]):
        return "I can help you take notes! Use the **Notes tab** in the sidebar to add, view, and manage your notes. They're saved in your browser's local storage."

    if any(w in lower for w in ["remind", "reminder", "alarm"]):
        return "I can set reminders! Use the **Reminders tab** in the sidebar. You can also type something like 'Remind me in 5 minutes to check email' in the chat."

    if any(w in lower for w in ["search", "google", "look up", "find"]):
        return "I can help you search! Use the **Web Search tab** in the sidebar, or I can try to answer your question directly. What would you like to know?"

    if any(w in lower for w in ["ai", "artificial intelligence", "machine learning", "deep learning"]):
        return "**Artificial Intelligence** is a broad field:\n\n- **Machine Learning**: Algorithms that learn from data (Random Forest, SVM, Neural Networks)\n- **Deep Learning**: Neural networks with many layers (CNN, RNN, Transformers)\n- **NLP**: Natural Language Processing (GPT, BERT, T5)\n- **Computer Vision**: Image recognition, object detection\n- **Applications**: Chatbots, self-driving cars, medical diagnosis, recommendations\n\nWhat aspect of AI interests you?"

    if any(w in lower for w in ["web", "website", "html", "css", "frontend"]):
        return "**Web Development** basics:\n\n- **HTML**: Structure and content\n- **CSS**: Styling and layout\n- **JavaScript**: Interactivity and logic\n- **Frameworks**: React, Vue, Angular, Bootstrap\n- **Backend**: Flask (Python), Express (Node.js), Django\n- **Deployment**: Vercel, Netlify, GitHub Pages, Render\n\nWhat would you like to learn about web development?"

    if any(w in lower for w in ["flask", "django", "fastapi"]):
        return "**Flask** is a lightweight Python web framework:\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello, World!'\n\napp.run()\n```\n\nIt's great for APIs and small-to-medium web apps. Anesh G J uses Flask for projects like Talentos and ProjectPop. Want to learn more about Flask?"

    return f"I understand you're asking about: *\"{message}\"*\n\nI'm SimonPeter AI, and I'm here to help! While I may not have an AI model connected right now, I have built-in knowledge on many topics:\n\n- **Science & Math** - Physics, chemistry, biology, calculations\n- **Programming** - Python, JavaScript, HTML/CSS, and more\n- **Cybersecurity** - Network security, cryptography, penetration testing\n- **Technology** - AI, web development, databases\n- **General Knowledge** - History, geography, current events\n\nTry asking me something specific! For example:\n- \"What is quantum computing?\"\n- \"Explain machine learning\"\n- \"How does HTTPS work?\"\n- \"Calculate 15% of 200\""


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Message required"}), 400

    ai_response = call_nvidia_ai(message, history)
    if ai_response:
        return jsonify({"response": ai_response, "source": "ai"})

    response = smart_fallback(message)
    return jsonify({"response": response, "source": "builtin"})


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "ai_model": NVIDIA_MODEL if NVIDIA_API_KEY else "builtin-only",
        "has_api_key": bool(NVIDIA_API_KEY),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
