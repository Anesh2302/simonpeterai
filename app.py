import os
import json
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder="static")
CORS(app)

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

SYSTEM_PROMPT = """You are SimonPeter AI, a highly knowledgeable, accurate, and helpful personal assistant created by Anesh G J. You are an expert across many domains.

CORE RULES:
1. ALWAYS give accurate, correct, and well-structured answers
2. Use markdown formatting: **bold** for emphasis, `code` for inline code, ```code blocks``` for multi-line code, and bullet lists
3. For math: show step-by-step solutions with the final answer clearly marked
4. For programming: provide working, correct code examples with explanations
5. For factual questions: give precise, accurate answers. If unsure, say so honestly
6. Be concise but thorough — don't leave out important details
7. If asked about time, date, weather, or calculator — provide the actual answer using your knowledge. For real-time weather, tell the user to use the Weather tab
8. Support multiple programming languages: Python, JavaScript, Java, C, C++, Go, Rust, SQL, HTML/CSS, TypeScript, and more
9. For cybersecurity questions: give detailed, accurate technical answers
10. For science, history, geography: provide well-sourced accurate information

DOMAINS OF EXPERTISE:
- General knowledge (science, history, geography, math, physics, chemistry, biology)
- Programming (Python, JavaScript, Java, C/C++, Go, Rust, TypeScript, SQL, HTML/CSS, and more)
- Web development (Flask, Django, React, Vue, Angular, Node.js, Express)
- Cybersecurity (network security, cryptography, penetration testing, OWASP, vulnerability analysis)
- Mathematics (algebra, calculus, statistics, linear algebra, discrete math)
- AI and machine learning
- Technology and software engineering
- Career advice and general life advice
- Current events and general knowledge

RESPONSE FORMAT:
- Start with a direct answer when possible
- Use markdown for structure (headers, bold, code blocks, lists)
- For code: always use ```language\ncode here\n``` fenced blocks
- For math: show work step by step
- End with a brief summary or offer to help further"""


def call_nvidia_ai(message, history=None):
    if not NVIDIA_API_KEY:
        return None

    now = datetime.now()
    context_msg = f"[Context: Current date is {now.strftime('%A, %B %d, %Y')}. Current time is {now.strftime('%I:%M %p %Z')}.]"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for h in history[-12:]:
            role = h.get("role", "user")
            if role not in ("user", "assistant"):
                role = "user"
            messages.append({"role": role, "content": h.get("content", "")})
    messages.append({"role": "user", "content": f"{context_msg}\n\n{message}"})

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
                "temperature": 0.5,
                "max_tokens": 2048,
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
    now = datetime.now()

    if any(w in lower for w in ["who are you", "what are you", "your name"]):
        return "I'm **SimonPeter AI**, a personal assistant created by **Anesh G J**. I'm powered by NVIDIA NIM AI and can help with programming, math, science, cybersecurity, general knowledge, and much more. What would you like to know?"

    if any(w in lower for w in ["who made you", "who created you", "your creator", "who built you"]):
        return "I was created by **Anesh G J**, a cybersecurity-focused full-stack developer from India. He built me as an AI-powered assistant using NVIDIA NIM integration. Check out his portfolio at [github.com/Anesh2302](https://github.com/Anesh2302)."

    greetings = ["hi", "hello", "hey", "sup", "yo", "hola", "good morning", "good evening", "good afternoon", "namaste"]
    if any(lower.startswith(g) for g in greetings):
        return f"Hey! I'm **SimonPeter AI**, your AI assistant. I can help with questions on any topic — programming, math, science, cybersecurity, general knowledge, and more. What would you like to know?"

    if any(w in lower for w in ["thank", "thanks", "thx", "appreciate"]):
        return "You're welcome! Feel free to ask me anything else. I'm here to help."

    if any(w in lower for w in ["bye", "goodbye", "see you", "later"]):
        return "Goodbye! It was great chatting with you. Come back anytime you need help!"

    if any(w in lower for w in ["help", "what can you do", "features", "capabilities"]):
        return """I can help you with many things:

**Knowledge & Education**
- Science, history, geography, math, physics, chemistry, biology
- Technology, AI, and programming
- Cybersecurity concepts and techniques

**Programming**
- Write and explain code in Python, JavaScript, Java, C/C++, Go, Rust, SQL, and more
- Debug code and explain errors
- Teach coding concepts step by step

**Math**
- Solve equations and show step-by-step work
- Statistics, calculus, algebra, geometry

**Tools**
- Weather updates (use the Weather tab)
- Notes and reminders
- Calculator
- Timer

**Conversation**
- General advice and career guidance
- Tech recommendations
- Discussion on any topic

Just ask me anything! I'll do my best to give you a helpful and accurate answer."""

    if any(w in lower for w in ["time", "what time", "current time"]):
        return f"The current time is **{now.strftime('%I:%M %p')}** on **{now.strftime('%A, %B %d, %Y')}**."

    if any(w in lower for w in ["date", "today", "what day"]):
        return f"Today is **{now.strftime('%A, %B %d, %Y')}**."

    if any(w in lower for w in ["weather", "temperature", "forecast"]):
        return "I can check the weather! Please use the **Weather tab** in the sidebar and enter your city name for real-time weather data."

    if any(w in lower for w in ["note", "remember", "write down"]):
        return "Use the **Notes tab** in the sidebar to add, view, and manage your notes. They're saved in your browser's local storage."

    if any(w in lower for w in ["remind", "reminder", "alarm"]):
        return "Use the **Reminders tab** in the sidebar. You can also type something like 'Remind me in 5 minutes to check email' in the chat."

    if any(w in lower for w in ["search", "google", "look up", "find"]):
        return "Use the **Web Search tab** in the sidebar to search Google directly, or just ask me — I can answer many questions directly!"

    if any(w in lower for w in ["joke", "funny", "laugh"]):
        import random
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache!",
            "What's a programmer's favorite hangout place? Foo Bar!",
            "Why do Java developers wear glasses? Because they can't C#!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why was the computer cold? It left its Windows open!",
            "A SQL query walks into a bar, sees two tables and asks... 'Can I JOIN you?'",
            "There are 10 types of people in the world: those who understand binary and those who don't.",
            "Why do Python programmers have low self-esteem? Because they're constantly comparing themselves to others with '==' instead of 'is'.",
        ]
        return random.choice(jokes)

    if "python" in lower:
        return "**Python** is one of the most popular programming languages. Here are key concepts:\n\n- **Syntax**: Clean and readable, uses indentation for blocks\n- **Data Types**: `int`, `float`, `str`, `list`, `dict`, `tuple`, `set`\n- **Libraries**: Flask (web), NumPy (math), Pandas (data), TensorFlow (AI)\n- **Example**:\n```python\nprint('Hello, World!')\n```\n\nWhat specific Python topic would you like to learn about?"

    if "javascript" in lower:
        return "**JavaScript** is the language of the web. Key concepts:\n\n- **ES6+**: Arrow functions, template literals, destructuring, async/await\n- **Frameworks**: React, Vue, Angular\n- **Node.js**: Server-side JavaScript\n- **Example**:\n```javascript\nconsole.log('Hello, World!');\n```\n\nWhat JavaScript topic interests you?"

    if any(w in lower for w in ["cyber", "security", "hack", "vulnerability", "penetration"]):
        return "**Cybersecurity** is a critical field. Key areas:\n\n- **Network Security**: Firewalls, IDS/IPS, VPNs\n- **Web Security**: XSS, SQL injection, CSRF prevention\n- **Cryptography**: AES, RSA, hashing (SHA-256), SSL/TLS\n- **Penetration Testing**: Reconnaissance, scanning, exploitation\n- **Defense**: Incident response, forensics, hardening\n\nWhat aspect of cybersecurity interests you?"

    if any(w in lower for w in ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"]):
        return "**Artificial Intelligence** is a transformative field:\n\n- **Machine Learning**: Algorithms that learn from data (Random Forest, SVM, Neural Networks)\n- **Deep Learning**: Neural networks with many layers (CNN, RNN, Transformers)\n- **NLP**: Natural Language Processing (GPT, BERT, T5)\n- **Computer Vision**: Image recognition, object detection\n- **Applications**: Chatbots, self-driving cars, medical diagnosis, recommendations\n\nWhat aspect of AI interests you?"

    if any(w in lower for w in ["flask", "django", "fastapi"]):
        return "**Flask** is a lightweight Python web framework:\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello, World!'\n\napp.run()\n```\n\nIt's great for APIs and small-to-medium web apps. Want to learn more about Flask?"

    if any(w in lower for w in ["math", "calculate", "compute", "equation"]):
        nums = re.findall(r'[\d.]+', lower)
        if "square" in lower and "root" in lower and nums:
            import math
            n = float(nums[0])
            return f"The square root of **{n}** is **{math.sqrt(n):.4f}**."
        if "square" in lower and nums:
            n = float(nums[0])
            return f"The square of **{n}** is **{n**2}**."
        if any(op in lower for op in ["+", "plus", "add"]):
            if len(nums) >= 2:
                return f"**{nums[0]} + {nums[1]} = {float(nums[0]) + float(nums[1])}**"
        if any(op in lower for op in ["-", "minus", "subtract"]):
            if len(nums) >= 2:
                return f"**{nums[0]} - {nums[1]} = {float(nums[0]) - float(nums[1])}**"
        if any(op in lower for op in ["*", "times", "multiply"]):
            if len(nums) >= 2:
                return f"**{nums[0]} x {nums[1]} = {float(nums[0]) * float(nums[1])}**"
        if any(op in lower for op in ["/", "divide", "divided"]):
            if len(nums) >= 2 and float(nums[1]) != 0:
                return f"**{nums[0]} / {nums[1]} = {float(nums[0]) / float(nums[1]):.4f}**"
        return "I can help with math! Try something like:\n- 'What is 25 + 37?'\n- 'Calculate 144 square root'\n- 'What is 15 times 8?'"

    if any(w in lower for w in ["web", "website", "html", "css", "frontend", "react", "vue", "angular"]):
        return "**Web Development** basics:\n\n- **HTML**: Structure and content\n- **CSS**: Styling and layout\n- **JavaScript**: Interactivity and logic\n- **Frameworks**: React, Vue, Angular, Bootstrap\n- **Backend**: Flask (Python), Express (Node.js), Django\n- **Deployment**: Vercel, Netlify, GitHub Pages, Render\n\nWhat would you like to learn about web development?"

    return f"I'm SimonPeter AI. I'm here to help with questions on any topic — programming, math, science, cybersecurity, and general knowledge.\n\nI notice you asked: *\"{message}\"*\n\nTry asking me something specific like:\n- 'What is quantum computing?'\n- 'Explain machine learning'\n- 'How does HTTPS work?'\n- 'Write a Python function to sort a list'\n- 'What is 15% of 200?'"


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
