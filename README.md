# Gemini-CLI
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

very flexible command-line interface (CLI) for Google Gemini

Gemini-CLI is an advanced command-line interface framework developed to interact with Google's Gemini native AI models. It improves workflows by combining bat-and-pop sessions with AI technology. Archive operations and Linux shell integration. Designed with penetration testers and developers in mind, Gemini-CLI gives users the ability to execute scripts, execute commands, and manage files completely.

## features

### 1. Interactive AI chat
- Engage in real-time conversations powered by Google's Gemini AI.
- Customize system commands for specific use cases, such as penetration testing or development.
- ```bash
  python geminicli.py -chat -m gemini-1.5-flash-001
### 2. Standalone Execution Mode:
- Execute single prompts against Gemini and save the response to a file. Ideal for batch processing or scripting.
- ```bash
  python geminicli.py -m gemini-1.5-pro-latest -p 'tell me a story' -o story.txt
### 3. Shell integration
- Create and execute Linux commands and scripts directly.
- Run automation and penetration testing procedures smoothly.
- ```bash
  python geminicli.py -shell

### 4. Session management
- Save, load and delete chat history for future reference or decluttering in -chat mode.

### 5. File operations
- Upload, list, and delete files via the Gemini API.
- Supports various file types such as `.txt`, `.csv`, `.py`, `.sh`, '.jpg'

### 6. Ideal flexibility
- Supports many models such as `gemini-1.5-flash` and `gemini-1.5-pro` for various needs.

### 7. Customization
- Configure default prompt System instructions and model parameters through `config.json` or any other you want.
- Configure prompt system instructions and other parameters using flags. -> python geminicli.py -h

## Installation
Follow these steps to install and set up Gemini-CLI:

### 1. Clone the Repository
```bash
git clone https://github.com/KaulikMakwana/Gemini-CLI.git
cd Gemini-CLI
pip install -r requirements.txt
python geminicli.py --help
```
### 2. Configure Environment Variables
```bash
export GEMINI_API_KEY="your_api_key_here"
> it would be good if you save it in .bashrc file
>> now you can run python geminicli.py --help
```

## Usages

### using config file.
you can use and customise using json config file for ease automation.
- python geminicli.py -c config.json

### using interactive chat session
- python geminicli.py -chat -m gemini-1.5-pro-latest
- **Inside the Interactive Chat:**
   - Use `@help` to see available commands.
   - Use `@upload_files` to upload files.
   - Use `@save_history` to save the chat history.
   - Use `@load_privious_history` to load a previous chat history.
   - Use `@delete_history` to delete chat history.
   - In the shell integration mode (`-shell`), provide prompts for Linux commands or penetration testing tasks.
   ![Demo](https://github.com/KaulikMakwana/Gemini-CLI/blob/main/demo/interactive.ogv)


### using standalone session
- python geminicli.py -p 'what is internet' -s 'you are expert in technology' -o internet.md
![Demo](https://github.com/KaulikMakwana/Gemini-CLI/blob/main/demo/stand_alone.ogv)

### with files
- python geminicli.py -p 'analyse uploaded file and tell me what can you see' -s 'you are expert in technology' -f 'demo.jpg' -o internet.md

### list and delete files
- python geminicli.py -lf -df

##Gemini-Cli 

```bash
~/myenv/bin/python geminicli.py --help                                                                                                                    ─╯
usage: gemini-cli [-h] [-p PROMPT] [--update] [-o OUTPUT] [-c CONFIG] [-s SYSTEM_INSTRUCTION] [-m MODEL] [-rm {text/plain,application/json}] [-top_p TOP_P]
                  [-top_k TOP_K] [-max_tokens MAX_OUTPUT_TOKENS] [-temp TEMPERATURE] [-f FILES] [-lf] [-df] [-chat] [-shell]

Google Gemini CLI...

options:
  -h, --help            show this help message and exit
  -p PROMPT, --prompt PROMPT
                        Prompt for Gemini.
  --update              Update Gemini CLI for a new version.
  -o OUTPUT, --output OUTPUT
                        Save Gemini response in a file.
  -c CONFIG, --config CONFIG
                        Configuration file for Gemini.

Model Configuration Options:
  -s SYSTEM_INSTRUCTION, --system_instruction SYSTEM_INSTRUCTION
                        Set system instruction for Gemini.
  -m MODEL, --model MODEL
                        Model to use for Gemini.
  -rm {text/plain,application/json}, --response_mimetype {text/plain,application/json}
                        Response MIME type for Gemini response.
  -top_p TOP_P, --top_p TOP_P
                        Set top_p.
  -top_k TOP_K, --top_k TOP_K
                        Set top_k.
  -max_tokens MAX_OUTPUT_TOKENS, --max_output_tokens MAX_OUTPUT_TOKENS
                        Set max output tokens.
  -temp TEMPERATURE, --temperature TEMPERATURE
                        Temperature for more creativity.

File-Related Options:
  -f FILES, --files FILES
                        Upload file to Gemini.
  -lf, --list_files     List all uploaded files from Gemini.
  -df, --delete_files   Delete all uploaded files from Gemini.

Interactive Chat Mode:
  -chat                 Enable interactive chat mode.

Shell Intigration:
  -shell                enable shell intigration where gemini can possible to automate your linux another tasks.

 [ℹ] Models Supported by gemini Listed below...
 [✔] Flash Models
gemini-1.5-flash, gemini-1.5-flash-001 , gemini-1.5-flash-001-tuning, gemini-1.5-flash-002,
gemini-1.5-flash-8b, gemini-1.5-flash-8b-001,  gemini-1.5-flash-8b-exp-0827, gemini-1.5-flash-8b-exp-0924,
gemini-1.5-flash-8b-latest,  gemini-1.5-flash-latest,
 [✔] Pro Models
gemini-1.5-pro,  gemini-1.5-pro-latest,  gemini-1.5-pro-001, gemini-1.5-pro-002,
gemini-2.0-flash-exp,
 [✔] 2.0 and experimental Models
gemini-2.0-flash-thinking-exp,  gemini-2.0-flash-thinking-exp-1219,  learnlm-1.5-pro-experimental,
```
![Interactive chat](https://github.com/KaulikMakwana/Gemini-CLI/blob/main/demo/interactive.png)
![cli](https://github.com/KaulikMakwana/Gemini-CLI/blob/main/demo/cli.png)
  
