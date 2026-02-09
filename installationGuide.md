# LCM GitHub Installation Guide

To install the **LCM** package directly from GitHub, follow the instructions below.

Note that since the repository is structured as a "wrapper" containing multiple folders, you need to point `pip` to the `lcm-code` subdirectory.

## 🚀 Installation Command

You can install the library directly using `pip` by pointing to your GitHub repository:

```bash
# Basic installation from GitHub
pip install git+https://github.com/Atul04singh/LCM_wrapper.git#subdirectory=lcm-code

# Installation with all dependencies (Ollama + Hugging Face)
pip install "lcm[all] @ git+https://github.com/Atul04singh/LCM_wrapper.git#subdirectory=lcm-code"
```

## 🛠️ Step-by-Step for New Projects

1. **Create a private environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install via GitHub**:
   _(Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub details)_

   ```bash
   pip install "lcm[all] @ git+https://github.com/Atul04singh/LCM_wrapper.git#subdirectory=lcm-code"
   ```

3. **Verify Installation**:
   ```bash
   python -c "from lcm import Model; print('LCM successfully installed!')"
   ```

---

_Created by the LCM Team._
_Atul Singh_
