<img src="img/bashimu.jpeg" alt="drawing" width="200"/>

### About
BASHIMU is a Python-based Terminal User Interface (TUI) for interacting with various AI models including OpenAI's ChatGPT, Anthropic's Claude, Google Gemini, and Ollama.
It provides both interactive chat sessions and quick command-line queries with customizable personas.


### Installation

#### Method 1: Using pip (Recommended)
```bash
pip install bashimu
```

Or install from source:
```bash
git clone https://github.com/wiktorjl/bashimu.git
cd bashimu
pip install .
```

After installation, configure your API keys by setting the appropriate environment variables:
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key"
```

### Usage

Interactive mode:
```bash
bashimu-tui
```

Non-interactive mode (new):
```bash
bashimu-tui "what is the current directory command"
bashimu-tui --provider openai "how to find files by name"
bashimu-tui --persona coding_mentor "explain git rebase"
```


### Demo:
<img src="img/bashimu_demo_2x.gif" width="800"/>
