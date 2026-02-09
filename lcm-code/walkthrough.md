# LCM (Lightweight Chat Model) - Comprehensive Walkthrough

LCM is designed to be the "one-stop-shop" for Python developers who want to switch between local and cloud AI models without rewriting their application logic. This guide covers how to use LCM for both **Ollama** and **Hugging Face**.

---

Regardless of which model you use, LCM provides three core functions in both **Asynchronous** and **Synchronous** flavors.

### Asynchronous (Modern Python)

Best for high-performance apps, web servers, and GUI apps. These require `await` and `asyncio`.

| Method                                 | Description                      |
| :------------------------------------- | :------------------------------- |
| `await model.chat(...)`                | Returns full response as string. |
| `async for token in model.stream(...)` | Yields tokens one by one.        |
| `await model.embed(...)`               | Returns vector embedding.        |

### Synchronous (Simple Scripting)

Best for simple automation scripts, data processing, or when you don't want to use `asyncio`. **No `await` or `async def` required.**

| Method                                | Description                      |
| :------------------------------------ | :------------------------------- |
| `model.chat_sync(...)`                | Returns full response as string. |
| `for token in model.stream_sync(...)` | Yields tokens one by one.        |
| `model.embed_sync(...)`               | Returns vector embedding.        |

---

## 2. Using LCM with Ollama

Ollama is treated as a **local-entry** provider. Your local Ollama server acts as the gateway for everything.

### Features

- **Auto-Pull**: If you request a model you don't have, LCM will automatically start downloading it.
- **Cloud Proxy**: If you use a model name with `-cloud` (e.g., `llama3-cloud`), your local server handles the cloud connection (requires `ollama login` via CLI).

### `.model` Configuration

Create a file named `.model` in your project root:

```ini
provider = ollama
model = gemma3:4b
runtime = local
stream = true
timeout = 120
base_url = http://localhost:11434  # Optional: defaults to this
```

### Full Example

```python
import asyncio
from lcm import Model

async def main():
    # Model name can be passed in Constructor or .model file
    model = Model("gemma3:4b")

    # 1. Chat
    print(await model.chat("Hi!"))

    # 2. Embed
    vec = await model.embed("Hello world")
    print(f"Vector size: {len(vec)}")

asyncio.run(main())
```

---

## 3. Using LCM with Hugging Face

Hugging Face has two distinct runtimes: **Cloud** (API) and **Local** (GPU/CPU).

### Case A: Hugging Face Cloud (Inference API)

Use this for instant access to huge models without using your own hardware.

**`.model` Configuration:**

```ini
provider = huggingface
runtime = cloud
hf_model = meta-llama/Llama-3.2-3B-Instruct
hf_token = your_hf_token_here
```

### Case B: Hugging Face Local (Transformers)

Use this for 100% private execution on your own GPU/CPU.

**`.model` Configuration:**

```ini
provider = huggingface
runtime = local
model = mbx/TinyLlama-1.1B-Chat-v1.0
device = cuda  # Options: 'cuda', 'mps' (Mac), 'cpu'
```

### Full Example

```python
import asyncio
from lcm import Model

async def main():
    # Switching to cloud via code override
    model = Model("Qwen/Qwen2.5-7B-Instruct", provider="huggingface", runtime="cloud")

    async for token in model.stream("Plan a 3-day trip to Paris."):
        print(token, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. Advanced: The `.model` File Reference

The `.model` file follows a simple `key = value` format. You can use environment variables inside it using `${VAR_NAME}` syntax.

| Key        | Description                     | Example                               |
| :--------- | :------------------------------ | :------------------------------------ |
| `provider` | `ollama` or `huggingface`       | `provider = ollama`                   |
| `model`    | The model name/ID               | `model = llama3`                      |
| `runtime`  | For HF only: `local` or `cloud` | `runtime = cloud`                     |
| `hf_token` | Your Hugging Face API key       | `hf_token = ${HF_TOKEN}`              |
| `base_url` | Custom API endpoint             | `base_url = http://192.168.1.5:11434` |
| `device`   | For HF Local: hardware target   | `device = cpu`                        |

### Configuration Priority

LCM resolves settings in this order (highest to lowest):

1.  **Constructor overrides**: `Model(model="xxx", provider="huggingface")` - _Explicit Way_
2.  **Project-level**: `.model` in your current folder.
3.  **User-level**: `.model` in your Home directory (`~/.model`).
4.  **Environment Variables**: e.g., `LCM_MODEL=xxx`.

---

## 5. Tips & Tricks

### Streaming Output Explanation

In the streaming examples, you'll see this line:
`print(token, end="", flush=True)`

- **`end=""`**: By default, `print()` adds a newline (`\n`) at the end. Setting this to empty ensures tokens appear next to each other in a single line.
- **`flush=True`**: Python's output is buffered. This forces the console to show the token _immediately_ rather than waiting for a full line, creating that smooth "AI character-by-character" effect.

---

---

## 6. Troubleshooting (Product Errors)

LCM doesn't just crash; it tells you how to fix the problem.

- **`RuntimeUnavailableError`**: Ollama server is likely down. **Fix**: Run `ollama serve`.
- **`AuthError`**: Your Hugging Face token is wrong or missing. **Fix**: Check your `.model` file for `hf_token`.
- **`ConfigError`**: There is a typo in your `.model` file. **Fix**: Ensure keys are lowercase and format is `key = value`.
