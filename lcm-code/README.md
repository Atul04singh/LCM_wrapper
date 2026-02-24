# 🚀 LCM: Lightweight Chat Model

**The effortless way to use open-source LLMs locally.**

LCM is a premium Python wrapper designed for developers who want the power of local and cloud LLMs without the boilerplate. It features a "Catchy API" that makes complex workflows feel like a walk in the park.

---

## ✨ Features

- **Catchy API**: Intuitive methods like `.ask()`, `.flow()`, and `.extract()`.
- **Fluent Chaining**: Build complex AI pipelines with `.pipe().then().jsononly`.
- **Express-like Middleware**: Intercept and modify message flows globally with `.use()`.
- **Zero Config**: Use `.model` files to swap providers and models without touching code.
- **Production Ready**: Built-in automatic retries, local JSON caching, and emoji-rich logging.
- **Multi-Provider**: Seamless support for **Ollama** and **Hugging Face** (Local & Cloud).

---

## 🛠️ Installation

```bash
git clone https://github.com/Atul04singh/LCM_wrapper.git
cd LCM_wrapper/lcm-code
pip install -e .[all]
```

---

## 🚀 Quick Start (The "Easy" Way)

### 1. Configure your logic in `.model`

```ini
provider = ollama
model = gemma3:latest
verbose = true
```

### 2. Run your AI

```python
from lcm import AI

ai = AI()
response = ai.ask("Explain quantum entanglement like I'm five.")
print(response)
```

---

## 📖 The Catchy API Reference

| Method            | Purpose          | Implementation Detail                          |
| :---------------- | :--------------- | :--------------------------------------------- |
| **`.ask()`**      | Simple Q&A       | Replaces `chat()`. Supports retries/caching.   |
| **`.flow()`**     | Streaming tokens | Yields words one by one for a smooth UI.       |
| **`.extract()`**  | Structured Data  | Automatically maps text to your JSON schema.   |
| **`.point()`**    | Word Embeddings  | Turns text into high-dimensional vector space. |
| **`.remember()`** | Session Memory   | Automates chat history management.             |
| **`.forget()`**   | Clear Brain      | Resets the conversation context.               |
| **`.peek()`**     | Health Check     | Beautifully prints the current AI status.      |
| **`.pipe()`**     | Start Chain      | Initiates a fluent processing flow.            |

---

## 🧱 Advanced Workflows

### 🔗 Fluent Chaining

Pass results from one task to another elegantly.

```python
result = await ai.pipe("Raw customer feedback text...") \
             .then("Summarize into a single sentence") \
             .then("Extract sentiment and key topics as JSON") \
             .jsononly
```

### 🏴‍☠️ Middleware

Modify every message before it reaches the AI.

```python
@ai.use
def pirate_middleware(messages):
    messages.insert(0, {"role": "system", "content": "Ye are a pirate captain."})
    return messages

ai.ask("How is the weather?") # "Arrr, the skies be clear today, matey!"
```

---

## ⚙️ Configuration (.model)

LCM looks for a `.model` file in your project or home directory.

**Ollama (Local):**

```ini
provider = ollama
model = llama3:8b
```

**Hugging Face (Cloud):**

```ini
provider = huggingface
runtime = cloud
model = mistralai/Mistral-7B-v0.1
hf_token = ${HF_TOKEN}
```

---

## 🏗️ Project Structure

- `src/lcm/`: Core logic and provider implementation.
- `tests/`: Comprehensive examples for every Catchy API feature.
- `walkthrough.md`: A detailed "book" for mastering LCM.

---

## 🤝 Contributing

We love contributions! Feel free to open issues or submit pull requests to make local AI even easier for everyone.

---

_Built with ❤️ for the open-source community._
