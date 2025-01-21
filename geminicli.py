#!/usr/bin/python3.12
import os,socket,argparse,textwrap
from prompt_toolkit import prompt, ANSI 
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from colorama import Fore, Style
import json,datetime,uuid 
from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# Terminal output styles
class Styles:
    INFO = f"{Fore.BLUE} [ℹ] "
    SUCCESS = f"{Fore.GREEN}{Style.BRIGHT} [✔] "
    FAILED = f"{Fore.RED} [✖] "
    ERROR = f"{Fore.LIGHTRED_EX}{Style.BRIGHT} [⚠] "
    WARNING = f"{Fore.YELLOW} [~] "
    PROMPT = f"{Fore.MAGENTA}"
    TEXT = f"{Fore.CYAN}"
    RESET = Style.RESET_ALL

class GeminiCLI:
    def __init__(self,prompt='Hello',system_instruction='you are penetration tester.',model_to_use="gemini-1.5-flash-002",
                response_mimetype="text/plain",files=None,output='response.txt',config_file='config.json',
                temperature=0.3,top_p=0.95,top_k=40,max_output_tokens=8192):

        self.prompt=prompt
        self.system_instruction=system_instruction
        self.files=files
        self.model_to_use=model_to_use
        self.response_mimetype=response_mimetype
        self.temperature=temperature
        self.top_p=top_p
        self.top_k=top_k 
        self.max_output_tokens=max_output_tokens
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_session = None
        self.output=output 
        self.config_file=config_file
    
    def configure_model(self):
        """Configures the Generative Model."""
        
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY')) 
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
        
        generation_config = {
                      "temperature": self.temperature,
                      "top_p": self.top_p,
                      "top_k": self.top_k,
                      "max_output_tokens": self.max_output_tokens,
                      "response_mime_type": self.response_mimetype,
                    }
        return genai.GenerativeModel(model_name=self.model_to_use,
                                       system_instruction=self.system_instruction,
                                       generation_config=generation_config,
                                       safety_settings=safety_settings,
                                       )
    
    def config(self):
        """Load configuration from a JSON file"""
        try:
            with open(self.config_file, 'r') as config_file:
                config_data = json.load(config_file)
                self.prompt=config_data['prompt']
                self.system_instruction = config_data['system_instruction']
                self.model_to_use = config_data['model_to_use']
                self.response_mimetype = config_data['response_mimetype']
                self.temperature = config_data['temperature']
                self.top_p = config_data['top_p']
                self.top_k = config_data['top_k']
                self.max_output_tokens = config_data['max_output_tokens']
                self.output=config_data['output']
                self.files=config_data['upload_files']

        except FileNotFoundError:
            print(f"{Styles.ERROR}Configuration file not found at {self.config_file}.{Styles.RESET}")
        except json.JSONDecodeError as e:
            print(f"{Styles.ERROR}Failed to parse config file: {e}{Styles.RESET}")
        except Exception as e:
            print(f"{Styles.ERROR}An error occurred while loading the config: {e}{Styles.RESET}")

        
    def file_operations(self,operation="list_files"):
        """Perform file operations such as listing or deleting files.
         - operation: default: list_files, delete_files
        """
        
        for file in genai.list_files():
            try:
                if operation == 'list_files':
                    print(f"{Styles.SUCCESS}File Listed: {file.display_name} {Styles.RESET}")
                elif operation == 'delete_files':
                    file.delete()
                    print(f"{Styles.SUCCESS}File {file.display_name} Deleted {Styles.RESET}")
                else:
                    print(f"{Styles.FAILED}Wrong argument...{Styles.RESET}")
            except Exception as e :
                print(f"{Styles.ERROR}File not found.. {e} {Styles.RESET}")

    def handle_file_uploads(self, paths):
        """
        Upload one or more files to Gemini API.
        - paths: A string (single file path) or a list of file paths.
        """
        uploaded_files = []
        try:
            # Ensure paths is a list for consistent processing
            if isinstance(paths, str):
                paths = [paths]

            mime_types = {
                ".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".webp": "image/webp",
                ".mp4": "video/mp4", ".py": "text/x-python",
                ".js": "text/javascript", ".html": "text/html",
                ".css": "text/css", ".md": "text/markdown",
                ".csv": "text/csv", ".txt": "text/plain",
            }

            for path in paths:
                
                _, ext = os.path.splitext(path)
                mimetype = mime_types.get(ext.lower(), "text/plain")
                try:
                    file = genai.upload_file(path, mime_type=mimetype)
                    print(f"{Styles.INFO}File Uploaded: {file.display_name}{Styles.RESET}")
                    uploaded_files.append(file)  
                except Exception as e:
                    print(f"{Styles.ERROR}Error in File Upload ({path}): {e}{Styles.RESET}")
                    
            if not uploaded_files:
                uploaded_files.append("_") 
        except Exception as e:
            print(f"{Styles.ERROR}Error during file upload processing: {e}{Styles.RESET}")
        return uploaded_files
    
    def cli(self, user_input, completer=['@help','@go_back','@exit']):
        """cli prompt for command line interface
         - user_input: user input (prompt)
         - completer: session_completer or history_completer
        """ 
        def key_binding():
            bindings = KeyBindings()
            
            @bindings.add("c-c")
            def _(event):
                exit()
            
            @bindings.add("enter")
            def _(event):
                event.app.exit(result=event.app.current_buffer.text)
            
            @bindings.add("c-n")
            def _(event):
                buffer = event.app.current_buffer
                buffer.insert_text("\n") 
            return bindings

        completer = WordCompleter(completer,ignore_case=True)
        c1='\033[35m'
        c2='\033[0m'
        Prompt = prompt(
            message=ANSI(f"{c1}:root@{user_input}>{c2}: "),
            multiline=True,
            key_bindings=key_binding(),
            completer=completer,
            )
        return Prompt
        
    def save_content(self,content, filename,mimetype='application/json', mode='w'):
        """Save content to a file.
         - content: content
         - filename: content file name
         - mimetype: content mimetype: default: application/json ; text/plain
         - mode: w ; a 
        """
        try:
            with open(filename, mode) as file:
                data=json.dumps(content) if mimetype == 'application/json' else content 
                file.write(data)
            print(f"{Styles.SUCCESS}Successfully saved to {filename}{Styles.RESET}")
        except Exception as e:
            print(f"{Styles.ERROR}Failed to save content: {e}{Styles.RESET}")

    def read_file_content(self,file,mimetype='application/json'):
        """Read content from a file.
         - file: file to be read 
         - mimetype: content mimetype: default: application/json ; text/plain
        """
        try:
            with open(file, 'r') as f:
                data=json.load(f) if mimetype == 'application/json' else f.read()
                return data 
        except Exception as e:
            print(f"{Styles.ERROR}Error reading file: {e}{Styles.RESET}")
            
    def save_chat_history(self, chat_history, filename=None, directory_path=os.path.expanduser("~/.gemini_chat_history")):
        """
        Save or append chat session history.

        Args:
            chat_history: The chat history object.
            filename: Optional; the filename to save the history.
            directory_path: Optional; the directory to save the history.
        """
        try:
            # Ensure the directory exists
            os.makedirs(directory_path, exist_ok=True)

            # Sanitize timestamp for filename usage
            sanitized_timestamp = self.timestamp.replace(":", "-").replace(" ", "_")

            # Determine if using a loaded session
            if self.current_session and not filename:
                # Use the current session's filename if it's already loaded
                filename = self.current_session["filename"]
            elif not self.current_session or (filename and filename != self.current_session.get("filename", "")):
                # Generate a new session ID and filename for a new session
                session_id = uuid.uuid4().hex[:8]
                filename = f"{session_id}_{sanitized_timestamp}_{filename or 'session'}.json"
                self.current_session = {"uuid": session_id, "filename": filename}

            filepath = os.path.join(directory_path, filename)

            # Load existing history if any
            if os.path.exists(filepath):
                save_history = self.read_file_content(filepath)  # Uses a predefined method
            else:
                save_history = []

            # Validate chat_history structure
            if not isinstance(chat_history, list) or not all(hasattr(x, "role") and hasattr(x, "parts") for x in chat_history):
                raise ValueError("chat_history must be a list of objects with 'role' and 'parts' attributes.")

            # Append new chat history
            save_history.extend({"role": x.role, "parts": [y.text]} for x in chat_history for y in x.parts)

            # Save the updated history
            self.save_content(content=save_history, filename=filepath,mode='a')

            # Save system instruction
            session_id, timestamp, *_ = filename.split('_')
            instruction_path = os.path.join(directory_path, f"{session_id}_{timestamp}-chat_instruction.system")

            if not os.path.exists(instruction_path):
                self.save_content(content=self.system_instruction, filename=instruction_path, mimetype='text/plain')

            print(f"{Styles.SUCCESS}Chat history saved successfully to {filename}.{Styles.RESET}")

        except Exception as e:
            print(f"{Styles.ERROR}Error saving chat history: {e} (Filename: {filename}, Directory: {directory_path}){Styles.RESET}")




    def load_privious_chat_history(self,directory_path = os.path.expanduser("~/.gemini_chat_history")):  
        """load privious chat history"""
        
        try:
            json_files = [file for file in os.listdir(directory_path) if file.endswith('.json')]
            if json_files:
                for num, file in enumerate(json_files):
                    print(f'{num}: {file}')
                while True:
                    choice = self.cli("[] load privious chat history by selecting number (or '@go_back' to return):")
                    if choice.lower() == '@go_back':
                        print("Returning to the previous menu...")
                        break  # Exit the loop and return to the previous menu
                    try: 
                        choice = int(choice)   
                        if 0 <= choice < len(json_files):
                            # file selection 
                            selected_file = json_files[choice]
                            session_id, timestamp, *_ = selected_file.split('_') # Extract session_id, timestamp ,_
                            # join directory and selected file.
                            file_path = os.path.join(directory_path, selected_file)
                            load_history=self.read_file_content(file_path) # load_history

                            instruction_filename = f'{session_id}_{timestamp}-chat_instruction.system'
                            instruction_path = os.path.join(directory_path, instruction_filename) #system instruction
                         
                            system_instruction=self.read_file_content(file=instruction_path,mimetype='text/plain')
                            self.system_instruction=system_instruction   # load system instruction
                            self.chat_session(load_history)         # load chat history
                            break 
                        else:
                            print(f"{Styles.ERROR}Invalid number. Please select a valid number from the list.{Styles.RESET}")
                            
                    except ValueError:
                        print(f"{Styles.ERROR}Please enter a valid number.{Styles.RESET}")
            else:
                print(f"{Styles.FAILED}No history files found in the directory.{Styles.RESET}")
    
        except FileNotFoundError:
            print(f"{Styles.FAILED}The directory {directory_path} does not exist.{Styles.RESET}")

    def delete_chat_history(self,directory_path = os.path.expanduser("~/.gemini_chat_history")):
        """delete chat history"""
        try:
            json_files = [file for file in os.listdir(directory_path) if file.endswith('.json')]
            if json_files:
                for num, file in enumerate(json_files):
                    print(f'{num}: {file}')
                while True:
                    choice = self.cli("delete chat history by selecting number (or '@go_back' to return):")
                    if choice.lower() == '@go_back':
                        print("Returning to the previous menu...")
                        break  # Exit the loop and return to the previous menu
                    try: 
                        choice = int(choice)   
                        if 0 <= choice < len(json_files):
                            selected_file = json_files[choice]
                            file_path = os.path.join(directory_path, selected_file)
                           
                            session_id, timestamp, *_ = selected_file.split('_') # Extract session_id, timestamp ,_
                           
                            instruction_filename = f'{session_id}_{timestamp}-chat_instruction.system'
                            instruction_path = os.path.join(directory_path, instruction_filename)
                           
                            os.remove(file_path)
                            os.remove(instruction_path)
                            break 
                        else:
                            print(f"{Styles.ERROR}Invalid number. Please select a valid number from the list.{Styles.RESET}")
                            
                    except ValueError:
                        print(f"{Styles.ERROR}Please enter a valid number.{Styles.RESET}")
            else:
                print(f"{Styles.FAILED}No history files found Probably already deleted..{Styles.RESET}")
    
        except FileNotFoundError:
            print(f"{Styles.FAILED}The directory {directory_path} does not exist.{Styles.RESET}")

    def chat_session(self,history=[]):
        """interactive cli for google gemini api"""
        try:
            print(f"{Styles.INFO} Gemini-cli ....{Styles.RESET}")
            print(f"""{Styles.PROMPT}- ctrl^c or @exit To exit. 
Press ctrl^n to new line and press enter to submit prompt.
Press @help for more information.
> @ and tab for command completion.
 {Styles.RESET}""")
            session_completer = ['@go_back','@help','@save_load_or_delete_history',
                                 '@upload_list_or_delete_files',
                                '@exit']
            history_help=['@save_history','@load_privious_history','@delete_history']
            files_help=['@upload_files','@list_uploaded_files','@delete_uploaded_files']

            uploaded_files = self.handle_file_uploads(self.files or [])
            model = self.configure_model()
            hostname = socket.gethostname()
            print(f'''
                    [{Styles.INFO}Model:{Styles.TEXT} {self.model_to_use}{Styles.RESET} ]  [{Styles.INFO}Top P:{Styles.TEXT} {self.top_p}{Styles.RESET} ]   [{Styles.INFO}Top k:{Styles.TEXT} {self.top_k}{Styles.RESET} ]
                    [{Styles.INFO}Response MimeType:{Styles.TEXT} {self.response_mimetype}{Styles.RESET} ] [{Styles.INFO}Max Token  {Styles.TEXT}{self.max_output_tokens}{Styles.RESET}]
                    [{Styles.INFO}Sytem Instruction:{Styles.TEXT}{self.system_instruction}{Styles.RESET}]
                      {Styles.RESET}
                    ''')
            for uploaded_file in uploaded_files:
                
                while True:
                    
                    chat = model.start_chat(history=history)
                    self.prompt=self.cli(user_input=hostname,completer=session_completer)
                    if self.prompt.startswith('@') and self.prompt in session_completer:

                        if self.prompt == '@save_load_or_delete_history':
                            self.prompt=self.cli(user_input="Select Options from [@save_history, @load_privious_history or @delete_history ?????]",completer=history_help)
                            
                            if self.prompt.startswith('@') and self.prompt in history_help:
                                if self.prompt == "@save_history":
                                    history_name=self.cli('Enter File Name:')
                                    self.save_chat_history(chat.history,filename=history_name)
                                
                                elif self.prompt == "@load_privious_history": 
                                    self.load_privious_chat_history()
                                elif self.prompt == "@delete_history":
                                    self.delete_chat_history()
                                
                        elif self.prompt == '@upload_list_or_delete_files':
                            self.prompt=self.cli(user_input="Select Options from [@upload_files, @list_uploaded_files or @delete_uploaded_files ?????]",completer=files_help)
                            if self.prompt.startswith('@') and self.prompt in files_help:
                            
                                if self.prompt == '@upload_files':
                                    file=self.cli("Upload Files to Gemini.. ").split()
                                    uploaded_file = self.handle_file_uploads(file)
                                    uploaded_files.extend(uploaded_file) 

                                elif self.prompt == "@list_uploaded_files": self.file_operations('list_files')
                                elif self.prompt == "@delete_uploaded_files": self.file_operations('delete_files')
                                
                        elif self.prompt == '@help':
                                print(f'''
{Styles.INFO} Functionality:{Styles.RESET}
{Styles.TEXT}   1. @save_load_or_delete_history {Styles.RESET}
{Styles.PROMPT}   -Sub options:{Styles.RESET}
     {Styles.TEXT}- @save_history: Saves the current chat history to a specified file.{Styles.RESET}
     {Styles.TEXT}- @load_privious_history: Loads the previously saved chat history.{Styles.RESET}
     {Styles.TEXT}- @delete_history: Deletes the chat history.{Styles.RESET}
{Styles.TEXT}   2. @upload_list_or_delete_files {Styles.RESET}
{Styles.PROMPT}    -Sub options:{Styles.RESET}
     {Styles.TEXT}- @upload_files: Allows the user to upload new files to the Gemini API.{Styles.RESET}
     {Styles.TEXT}- @list_uploaded_files: Lists the files that are currently uploaded.{Styles.RESET}
     {Styles.TEXT}- @delete_uploaded_files: Deletes files that were uploaded.{Styles.RESET}
{Styles.TEXT}- @exit: Exits the chat session.{Styles.RESET}
{Styles.TEXT}- @go_back: just take one step back{Styles.RESET}
{Styles.TEXT}- @help: show this help{Styles.RESET}
{Styles.PROMPT}- ctrl^c or @exit To exit. Press ctrl^n to new line and press enter to submit prompt. {Styles.RESET}''')
                                 
                        elif self.prompt == '@go_back':
                            break 
                        elif self.prompt == '@exit':
                            quit()
                      
                        else:print(f'{Styles.ERROR}Wrong command...see @help{Styles.RESET}')

                    else: 
                        
                        self.prompt = self.prompt if self.prompt else '.'  
                        response = chat.send_message([self.prompt, *uploaded_file],
                        stream=True,
                        request_options=RequestOptions(
                            retry=retry.Retry(initial=10, multiplier=2, maximum=60, timeout=300),))
                        print(f"{Styles.PROMPT}:root@Gemini> {Styles.RESET}")
                        for chunk in response:
                            print(f"{Styles.TEXT}{chunk.text} {Styles.RESET}",end="")
                        
                        history.append({"role":"user","parts":[self.prompt]})
                        history.append({"role":"model","parts":[response.text]}) 
                    
        except Exception as e:
            print(f"{Styles.ERROR}Error in AI Model:{e} {Styles.RESET}")

    def run_model(self):
        """stand alone session for gemini..."""
        try:
            
            model = self.configure_model()
            uploaded_files = self.handle_file_uploads(self.files or [])

            for uploaded_file in uploaded_files:
                
                self.prompt = self.prompt if self.prompt else '.' 
                response = model.generate_content([self.prompt, uploaded_file],
                        stream=True,
                        request_options=RequestOptions(
                            retry=retry.Retry(initial=10, multiplier=2, maximum=60, timeout=300),))
                print(f"{Styles.PROMPT}:root@Gemini> {Styles.RESET}")
                
                for chunk in response:
                    print(f"{Styles.TEXT}{chunk.text} {Styles.RESET}",end="")
                
                if self.output:
                    self.save_content(content=response.text,filename=self.output,mimetype=self.response_mimetype)
            
        except Exception as e:
            print(f"{Styles.ERROR}Error in AI Model: {e}{Styles.RESET}")

    def argsarguments(self):
        """Arguments parser for Gemini CLI."""
        parser = argparse.ArgumentParser(
            prog="gemini-cli",
            formatter_class=argparse.RawTextHelpFormatter,
            description=f"{Styles.TEXT}Google Gemini CLI...{Styles.RESET}",
            epilog=textwrap.dedent(f'''
{Styles.INFO}Models Supported by gemini Listed below...{Styles.RESET}
{Styles.SUCCESS}Flash Models{Styles.RESET}
{Styles.TEXT}gemini-1.5-flash, gemini-1.5-flash-001 , gemini-1.5-flash-001-tuning, gemini-1.5-flash-002,
gemini-1.5-flash-8b, gemini-1.5-flash-8b-001,  gemini-1.5-flash-8b-exp-0827, gemini-1.5-flash-8b-exp-0924,
gemini-1.5-flash-8b-latest,  gemini-1.5-flash-latest,{Styles.RESET}
{Styles.SUCCESS}Pro Models{Styles.RESET}
{Styles.TEXT}gemini-1.5-pro,  gemini-1.5-pro-latest,  gemini-1.5-pro-001, gemini-1.5-pro-002,
gemini-2.0-flash-exp,{Styles.RESET}
{Styles.SUCCESS}2.0 and experimental Models{Styles.RESET}
{Styles.TEXT}gemini-2.0-flash-thinking-exp,  gemini-2.0-flash-thinking-exp-1219,  learnlm-1.5-pro-experimental, {Styles.RESET}
{Styles.RESET}
            ''')
        )

        parser.add_argument("-p", "--prompt", default="arigato", type=str, help="Prompt for Gemini.")
        parser.add_argument("--update", action="store_true", help="Update Gemini CLI for a new version.")
        parser.add_argument("-o", "--output", type=str, help="Save Gemini response in a file.")
        parser.add_argument("-c", "--config", type=str, help="Configuration file for Gemini.")

        # Model Configuration Options
        model_config = parser.add_argument_group(f"{Styles.TEXT}Model Configuration Options{Styles.RESET}")
        model_config.add_argument("-s", "--system_instruction", default="you are gojo satoru!!!",
                                type=str, help="Set system instruction for Gemini.")
        model_config.add_argument("-m", "--model", type=str, default="gemini-1.5-flash-002",
                                help="Model to use for Gemini.")
        model_config.add_argument("-rm", "--response_mimetype", type=str, help="Response MIME type for Gemini response.",
                                default="text/plain", choices=["text/plain", "application/json"])
        model_config.add_argument("-top_p", "--top_p", default=0.95, type=float, help="Set top_p.")
        model_config.add_argument("-top_k", "--top_k", default=40, type=float, help="Set top_k.")
        model_config.add_argument("-max_tokens", "--max_output_tokens", default=8192, type=int, help="Set max output tokens.")
        model_config.add_argument("-temp", "--temperature", default=0.3, type=float, help="Temperature for more creativity.")

        # File-Related Options
        file_options = parser.add_argument_group(f"{Styles.TEXT}File-Related Options{Styles.RESET}")
        file_options.add_argument("-f", "--files", type=str, help="Upload file to Gemini.")
        file_options.add_argument("-lf", "--list_files", action="store_true", help="List all uploaded files from Gemini.")
        file_options.add_argument("-df", "--delete_files", action="store_true", help="Delete all uploaded files from Gemini.")

        # Chat Options
        chat_group = parser.add_argument_group(f"{Styles.TEXT}Interactive Chat Mode{Styles.RESET}")
        chat_group.add_argument("-chat", action="store_true", help="Enable interactive chat mode.")

        # Gems
        shell_group = parser.add_argument_group(f"{Styles.TEXT}Shell Intigration{Styles.RESET}")
        shell_group.add_argument("-shell",action="store_true",help="enable shell intigration where gemini can possible to automate your linux another tasks.") 

        args = parser.parse_args()

        # Validate arguments
        if args.chat:
            if args.prompt != "arigato" or args.files or args.list_files or args.delete_files or args.config:
                parser.error(f"{Styles.FAILED}-chat cannot be used with --prompt, --files, --list_files, --config or --delete_files.{Styles.RESET}")
        elif not args.prompt and not args.files and not args.list_files and not args.delete_files:
            parser.error(f"{Styles.FAILED}Either --prompt or file-related options must be provided when -chat is not used.{Styles.RESET}")

        if args.files and not os.path.exists(args.files):
            parser.error(f"{Styles.FAILED}File {args.files} not found. Please provide a valid file path.{Styles.RESET}")

        if args.config and not os.path.exists(args.config):
            parser.error(f"{Styles.FAILED}Configuration file {args.config} not found.{Styles.RESET}")

        return args

        
    def main(self):
        """main"""
        args=self.argsarguments()
        geminicli=GeminiCLI(
        prompt=args.prompt,
        system_instruction=args.system_instruction,
        model_to_use=args.model,
        response_mimetype=args.response_mimetype,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        max_output_tokens=args.max_output_tokens,
        files=args.files,
        output=args.output,
        config_file=args.config
        )

        if args.config:
            geminicli.config()

        if args.shell:
            from Gems import shell_helper
            shell_helper.main(model_to_use=args.model)
        if args.chat:
            geminicli.chat_session()
        else:
            if args.prompt:
                geminicli.run_model()

            if args.list_files:
                geminicli.file_operations("list_files")

            if args.delete_files:
                geminicli.file_operations("delete_files")

if __name__ == '__main__':
    
    gemini=GeminiCLI()
    gemini.main()