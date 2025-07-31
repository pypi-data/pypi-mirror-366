<img src="img/bashimu.jpeg" alt="drawing" width="200"/>

### About
BASHIMU is a simple bash script to interact with OpenAI's ChatGPT models.
It allows you to ask a question in the command line and get a one-liner response as a result.


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

#### Method 2: Using the deployment script
```bash
curl -s https://raw.githubusercontent.com/wiktorjl/bashimu/refs/heads/main/deploy.sh | sh
```

#### Method 3: Manual setup
Clone this repository and run ```bashimu_setup.sh``` script. It will set up the following variables:

```
$OPENAI_API_KEY - your private key
$OPENAI_MODEL_NAME - the default OpenAI model to be used
```

It will also ask you where to deploy the script, adjust the PATH accordingly, and set up ```?``` as an alias for ```bashimu.sh```.
Please view the script's source code before you run it so you know what it is doing.

### Usage

#### Bash Script
Executing a query: ```? get current time```

Executing the last suggested command: ```? !```

#### Python TUI (Terminal User Interface)

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
