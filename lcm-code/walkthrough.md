# 📖 The Catchy API Book: Master LCM in Minutes

Welcome to the definitive guide for LCM. This book covers every method in our "Catchy API" suite, designed to make local LLM development feel like magic. 🪄

---

## 🗂️ Table of Contents

0. [Pre-requisite: The .model File](#0-pre-requisite-the-model-file)
1. [AI.ask() - Common Sense Chat](#1-aiask---common-sense-chat)
2. [AI.flow() - The Token Streamer](#2-aiflow---the-token-streamer)
3. [AI.extract() - Data Digging](#3-aiextract---data-digging)
4. [AI.point() - Coordinate Space](#4-aipoint---coordinate-space)
5. [AI.peek() - The Health Monitor](#5-aipeek---the-health-monitor)
6. [AI.remember() & AI.forget() - Memory Control](#6-airemember--aiforget---memory-control)
7. [AI.pipe() - Flow Chaining](#7-aipipe---flow-chaining)
8. [AI.use() - Middleware Superpowers](#8-aiuse---middleware-superpowers)

---

## 🚀 The Catchy API at a Glance

| Method            | What it does      | Why it's cool                               |
| :---------------- | :---------------- | :------------------------------------------ |
| **`.ask()`**      | Quick answers     | Replaces boring `chat`                      |
| **`.flow()`**     | Stream tokens     | Smooth character-by-character effect        |
| **`.extract()`**  | Get JSON data     | No more manual parsing                      |
| **`.point()`**    | Vector Embeddings | Turn text into space-coordinates            |
| **`.peek()`**     | Health Check      | See if your "brain" is ready                |
| **`.remember()`** | Enable Memory     | Keeps track of the conversation             |
| **`.forget()`**   | Clear History     | Fresh start                                 |
| **`.pipe()`**     | Chaining          | Connect tasks like blocks                   |
| **`.use()`**      | Middleware        | Intercept & modify messages (Express style) |

---

## 0. Pre-requisite: The .model File

Before you write a single line of Python, LCM needs to know which "brain" to use. We do this with a `.model` file. It's like a `.env` file, but for LLMs.

### Why use a `.model` file?

- **Zero Config in Code**: Your Python scripts stay clean and focused on logic.
- **Easy Swapping**: Change from Ollama to Hugging Face by editing one word in one file.
- **Secure**: Interpolate environment variables for sensitive tokens.

### 📝 The .model File (Ollama Example)

For local-first development with Ollama.
Create a `.model` file in your project folder:

```ini
provider = ollama             # Use Ollama engine
model = gemma3:latest         # The model you pulled via CLI
stream = true                 # Default to smooth token streaming
timeout = 60                  # Wait for 60s before timing out
```

### 📝 The .model File (Hugging Face Example)

For running models from the HF Hub, either locally or via the Cloud API.

```ini
provider = huggingface        # Use Hugging Face engine
model = mistralai/Mistral...  # The HF model ID
runtime = cloud               # Options: 'cloud' (Inference API) or 'local'
hf_token = ${HF_TOKEN}        # Load token from your system ENV
device = cuda                 # For 'local' runtime: cuda, mps, or cpu
```

### 🔍 Search Priority (Where does LCM look?)

1. **Explicit Way**: `AI(model="...")` (Highest priority)
2. **Local Way**: `./.model` (In your current project folder)
3. **Global Way**: `~/.model` (In your Home folder for default settings)
4. **Environment Way**: `LCM_PROVIDER=ollama` (System-wide variables)

---

## 1. AI.ask() - Common Sense Chat

**Purpose**: The bread and butter of AI interaction. Use this when you want a straightforward answer to a question.

**Why it's cool**: It replaces the generic `chat` method with something more human. It automatically handles prompt normalization and context (if enabled).

### 💻 Example

```python
from lcm import AI

ai = AI()
answer = ai.ask("What is the most popular programming language in 2026?")
print(answer)
```

---

## 2. AI.flow() - The Token Streamer

**Purpose**: For real-time applications where waiting for a full paragraph is too slow.

**Why it's cool**: It gives that "AI is typing" effect. It works BOTH in `async` (for web servers) and `sync` (for simple terminal scripts).

### 💻 Example (Sync)

```python
ai = AI()
for token in ai.flow_sync("Tell me a story about a dragon"):
    print(token, end="", flush=True)
```

### 💻 Example (Async)

```python
import asyncio
from lcm import AI

async def stream_data():
    ai = AI()
    async for token in ai.flow("Tell me a story about a robot"):
        print(token, end="", flush=True)

asyncio.run(stream_data())
```

---

## 3. AI.extract() - Data Digging

**Purpose**: To get structured data (JSON) out of a mess of text.

**Why it's cool**: You don't need to write regex or tell the AI "Respond only with JSON" ten times. Just pass a schema, and LCM handles the heavy lifting.

### 💻 Example

```python
ai = AI()
schema = {"capital": "string", "population": "number"}
data = await ai.extract("Japan is an island country in East Asia.", schema=schema)
# Output: {"capital": "Tokyo", "population": 125000000}
```

---

## 4. AI.point() - Coordinate Space

**Purpose**: Turning text into a vector (a list of numbers) for search and memory systems.

**Why it's cool**: It simplifies the complex field of "embeddings" into a single command. You are "pointing" to a location in the AI's semantic map.

### 💻 Example

```python
vec = await ai.point("The future of artificial intelligence")
print(f"Vector Dimensions: {len(vec)}")
```

---

## 5. AI.peek() - The Health Monitor

**Purpose**: To check if your local AI is ready to talk.

**Why it's cool**: No more cryptic connection errors. `peek()` tells you exactly which model is loaded, which provider is running, and if everything is "Ready 🚀".

### 💻 Example

```python
ai = AI()
await ai.peek()
# --- AI Status ---
# Model:  gemma3:latest
# Provider: ollama
# Status:  Ready 🚀
```

---

## 6. AI.remember() & AI.forget() - Memory Control

**Purpose**: To make the AI "human-like" by remembering what you said earlier.

**Why it's cool**: You can turn memory on and off with one word. No need to manage complex "history" lists yourself.

### 💻 Example

```python
ai = AI().remember()
ai.ask("My cat's name is Luna.")
print(ai.ask("What is my cat's name?")) # "Your cat's name is Luna."

ai.forget() # Reset the AI's brain
```

---

## 7. AI.pipe() - Flow Chaining

**Purpose**: To connect multiple processing steps together in one readable line.

**Why it's cool**: Inspired by Unix pipes, it allows you to pass data from one AI task to another. Use `.then()` to continue and `.jsononly` to finish!

### 💻 Example

```python
raw_data = "Apple Inc. released a new phone today. Stocks went up 5%."

result = await ai.pipe(raw_data) \
             .then("Summarize this news into 1 sentence") \
             .then("Extract the company name and stock change as JSON") \
             .jsononly

print(result) # {'company': 'Apple Inc.', 'change': '+5%'}
```

---

## 8. AI.use() - Middleware Superpowers

**Purpose**: To intercept and modify messages before they hit the AI (preprocessing).

**Why it's cool**: Just like Express.js, you can add "layers" to your AI. Useful for security (cleaning PII), logging, or injecting hidden system instructions.

### 💻 Example

```python
@ai.use
def add_persona(messages):
    messages.insert(0, {"role": "system", "content": "You are a professional chef."})
    return messages

print(ai.ask("How do I boil an egg?")) # Answer will be chef-style!
```

---

_You have reached the end of the guide. Now go build something amazing!_ 🚀
