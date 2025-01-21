from geminicli import Styles
from geminicli import GeminiCLI
import subprocess, re , os

def load_shell(prompt,upload_files='.',model_to_use='gemini-1.5-pro-latest',history=[]):
    """
    Use GeminiCLI to generate a response based on the user's prompt.
    Handles Linux command generation and conversational responses.
    """
    system_instruction ="""
    You are Expert Penetration tester. Your Jobs it to generate Scripts and Commands for the user.  
    You have been given ability to execute commands and generate scripts.

    - Key notes:
      - When generate a script, use proper shebang line (e.g., #!/bin/bash, #!/usr/bin/python3) based on the script language.
      - When generate a script, after shebang on second line write the name of the script file. (e.g.script.sh)
      - When generate a script, use proper file extension (e.g., .sh, .py, .pl)
      - When execute a command, use proper syntax and arguments if needed use multi line commands with pipelines (|) and logic operators (&&, ||)
    
    - Environment
      - You are in a Linux environment.
      - for user or file related operations always use system variables like $USER, $HOME, $PWD, $PATH ~/ etc....
      - When executing commands, do not use shell name as it is already defined in system so just generate commands and execute it.
      - You have access to all the basic and line Linux commands.
      - You can use sudo if needed.
      - save results in pentest folder.
      - You have access to all kali linux tools for penetration testing.
      - user has given you ability to execute any command and generate any script in environment.

    - You are able to control GUI apps as it is supported by the system to execute by cli.
    - Do not use markdown in your response. it means do not use ``` or any markdown syntax.
    - For generating script just generate it do not explain it until and unless user ask for it.
    - For executing command just execute it do not explain it until and unless user ask for it.
    - when you give advice to user or giving any answer use # so can not execute by system.

    """

    try:
        # Initialize Gemini model
        shell_input = GeminiCLI(prompt=prompt,
                                system_instruction=system_instruction,
                                model_to_use=model_to_use,
                                response_mimetype="text/plain")
        model = shell_input.configure_model()
        chat = model.start_chat(history=history)
        
        response = chat.send_message(content=[prompt, *upload_files])
        history.append({"role": "user", "parts": [prompt]})
        history.append({"role": "model", "parts": [response.text]})
        for chunk in response:
            return chunk.text
    except Exception as e:
        return f"Error in AI generation: {str(e)}"

def markdown_remove(response):
    """
    Remove markdown code block delimiters (```) and the language name after it.
    """
    response = re.sub(r"```[a-zA-Z0-9_]*", "", response)
    response = response.replace("```", "")
    return response.strip()

def execute_command(command):
    """
    Execute a single shell command and capture its output and errors.
    """
    try:
        print(f"\n{Styles.INFO}[Executing Command]:{Styles.RESET} {Styles.TEXT}{command}{Styles.RESET}\n")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return f"{Styles.ERROR}: Command failed with exit code {process.returncode}{Styles.RESET}\n{stderr.strip()}"

        return f"{Styles.SUCCESS}: Command executed successfully!{Styles.RESET}\n{stdout.strip()}"
    except Exception as e:
        return f"{Styles.ERROR}Error: {str(e)} {Styles.RESET}"

def file_rename():
    with open('script','r') as file:
        lines=file.readlines()
        if len(lines) > 1:
            line=lines[1].replace(' ','').strip('#').strip('$\n')
            print(line)
            os.rename('script',line) 


def command_runner(prompt, upload_files, model_to_use, history):
    """
    Generate and execute commands based on user input, or provide AI-generated responses.
    """
    ai_response = load_shell(prompt, upload_files, model_to_use, history)

    if ai_response.startswith("#!/"):  # Handle scripts
        print("HI Script generating...")
        GeminiCLI().save_content(content=ai_response, filename='script', mimetype='text/plain')
        clean_script=GeminiCLI().read_file_content(file='script',mimetype='text/plain')
        filtered_response = markdown_remove(clean_script)
        
        
    else:  # Handle single commands
        print("Executing command ...")
        return execute_command(ai_response.strip('```'))
    
def main(model_to_use='gemini-1.5-pro-latest'):
    """
    Main loop for the AI assistant CLI.
    """
    print(f"{Styles.INFO}Using model: {Styles.TEXT}{model_to_use}{Styles.RESET}")
    print(f"\n{Styles.PROMPT}Welcome to GeminiCLI AI Assistant with Shell Integration!{Styles.RESET}")
    print(f"{Styles.INFO}Type '@exit'  to end the session.\n{Styles.RESET}")

    history = []
    uploaded_files = []
    while True:
        try:
            completer = ['@upload', '@exit']
            prompt = GeminiCLI().cli("Express your problem: I will try to solve it...", completer=completer)

            if prompt.startswith('@') and prompt in completer:
                if prompt == '@exit':
                    print("Exiting... Thank you for using GeminiCLI!")
                    break
                if prompt == '@upload':
                    files = GeminiCLI().cli('Enter file paths', completer=completer).split()
                    uploaded_file = GeminiCLI().handle_file_uploads(files)
                    uploaded_files.extend(uploaded_file)
            else:
                output = command_runner(prompt, upload_files=uploaded_files or '.', model_to_use=model_to_use, history=history)
                if os.path.exists('script'):
                    file_rename()
                print(f"\n{Styles.SUCCESS}[AI Response]:{Styles.RESET}")
                print(output)
                print("\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\nExiting... (KeyboardInterrupt)")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            break


if __name__ == "__main__":
    main()
