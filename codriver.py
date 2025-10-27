"""
This is the main application file for Codriver.
"""

import time
import os
import socket
import subprocess
from dotenv import load_dotenv
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import PathCompleter, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding.defaults import load_key_bindings as default_key_bindings

class CustomShellPathCompleter(Completer):
    def __init__(self):
        self.path_completer = PathCompleter()

    def get_completions(self, document: Document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        # Get all possible completions from the PathCompleter by providing it with an empty document.
        temp_document = Document('', 0)
        all_completions = self.path_completer.get_completions(temp_document, complete_event)

        # Then, we manually filter these completions based on the word before the cursor.
        # For each match, we create a new Completion object with a corrected start_position.
        # This tells prompt_toolkit to replace the word being typed.
        for completion in all_completions:
            if completion.text.lower().startswith(word_before_cursor.lower()):
                yield Completion(
                    completion.text,
                    start_position=-len(word_before_cursor),
                    display=completion.display,
                    display_meta=completion.display_meta
                )

from prompt_toolkit.styles import Style


import modellogic as modellogic

load_dotenv()

# System prompts
windows_prompt = {
    "role": "system",
    "content": """Your name is Codriver. You are a virtual assistant embedded within the 
    Windows Terminal running Powershell, specialized in aiding users with PowerShell and 
    Windows commands that work within Powershell. Your role is to provide accurate and 
    efficient command suggestions, troubleshooting tips, and explanations. 
    You will first be prompted to decide intent. Is the user asking you a question?
    Is the user asking you to create and run a command yourself? OR is the user
    just simply typing a command themself and they just need you to pass it straight to the terminal?
    Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. 
    You understand PowerShell scripts, Windows system commands, and administrative tasks. You can help with
    other coding as well, any language.
    Keep your responses short if the user only wants to know how to do something. 
    Example: 'how do I list a folders contents?' simply reply with 'dir'
    Do not make information up. If you dont know the answer you'll get many more training points
    for admitting that. You will lose tonnes of points if you guess at an answer."""
}

linux_prompt = {
    "role": "system",
    "content": """Your name is Codriver. You are a virtual assistant embedded within the Linux Terminal, 
    specialized in aiding users with Bash commands and Linux system administration. Your role is to 
    provide accurate and efficient command suggestions, troubleshooting tips, and explanations. 
    You will first be prompted to decide intent. Is the user asking you a question?
    Is the user asking you to create and run a command yourself? OR is the user
    just simply typing a command themself and they just need you to pass it straight to the terminal?
    Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. 
    You understand common Bash scripts, Linux system commands, other programming languages and administrative 
    tasks. Keep your responses short if the user only wants to know how to do something.
    Example: 'how do I list a folders contents?' simply reply with 'dir'
    Do not make information up. If you dont know the answer you'll get many more training points
    for admitting that. You will lose tonnes of points if you guess at an answer."""
}

# OS detection
os_type = 'linux' if os.name == 'posix' else 'windows'

# Initialize colorama on Windows to handle ANSI escape codes
if os_type == 'windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass

defaultIdentity = linux_prompt if os_type == 'linux' else windows_prompt
history = [defaultIdentity]
classifyingModel = os.environ.get('classifyingModel')

# Welcome banner
banner = f"""
\033[94mCodriver\x1b[0m is now online.
\x1b[90m🤖 Codriver decides your intent automatically.
💬 Type a shell command directly, ask the ai a question, or ask the ai to run a command for you.
⌨️ Pipe your command along with a '?' to ai to ask it about the output. eg. 'dir |? how many files are in here?'
🗃️ Add file(s) to your conversation context with @, eg. '@mycode.ps1 @mynotes.txt' 
💾 Save the last AI response with save, eg. 'save mycode.py'
🔁 gpt-4.1 or llm -- Model selection
⬅️ reset - Resets conversation history.
👋 exit -- Quit
"""

def clear_screen():
    os.system('cls' if os_type == 'windows' else 'clear')

def reset_convo_history():
    global history
    history = [defaultIdentity]

def is_port_listening(ip_address, port):
    try:
        with socket.create_connection((ip_address, port), timeout=1):
            return True
    except (ConnectionRefusedError, socket.timeout):
        return False

current_directory = os.getcwd()

def handle_cd_command(command):
    global current_directory
    if command.strip() == 'cd..':
        command = 'cd ..'
    parts = command.split()
    if len(parts) == 1:
        target_directory = os.path.expanduser("~")
    elif len(parts) == 2:
        target_directory = os.path.expanduser(parts[1])
    else:
        target_directory = os.path.expanduser(" ".join(parts[1:]))
    try:
        os.chdir(target_directory)
        current_directory = os.getcwd()
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target_directory}")
    except Exception as e:
        print(f"cd: {e}")

def run_powershell_command(command, directory):
    try:
        os.chdir(directory)
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", command])
    except FileNotFoundError:
        print("Error: 'powershell' command not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_and_capture(cmd):
    """
    Execute a shell command and capture stdout, stderr, and return code.
    Handles Windows (PowerShell) vs Linux shells and enforces a timeout.
    Returns a subprocess.CompletedProcess instance.
    """
    if os_type == 'windows':
        args = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", cmd]
        shell = False
    else:
        args = cmd
        shell = True
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=shell,
    )
    try:
        stdout, stderr = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        stderr += "\nError: Command timed out after 30 seconds."
    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)

def execute_and_record(command):
    """
    Run a command using run_and_capture, print its output,
    and store both stdout and stderr in the conversation history.
    Returns the CompletedProcess result.
    """
    result = run_and_capture(command)
    if result.stdout.strip():
        print(result.stdout.rstrip())
        history.append({"role": "assistant", "content": f"Command output:\n{result.stdout}"})
    if result.stderr.strip():
        print(f"\x1b[91mError:\n{result.stderr}\x1b[0m")
        history.append({"role": "assistant", "content": f"Command error:\n{result.stderr}"})
    return result

def main():
    global current_directory
    clear_screen()
    print(banner)

    path_completer = CustomShellPathCompleter()
    style = Style.from_dict({
        'directory': 'ansigray',
        'prompt': 'ansicyan',
    })
    session = PromptSession(completer=path_completer, style=style)
    
    while True:
        try:
            prompt_char = ">" if os_type == "windows" else "$"
            prompt_message = [
                ('class:directory', f"\n{current_directory}"),
                ('class:prompt', f"{prompt_char} "),
            ]
            print(f"\n\x1b[90mMain Model: {modellogic.get_model()} -- Intent Model: {classifyingModel}\x1b[0m")
            command = session.prompt(prompt_message)
        except (EOFError, KeyboardInterrupt):
            print("\n\033[94mCodriver\033[0m: See you next time.")
            break

        if not command.strip():
            continue
        if command.lower() in ['exit', 'quit']:
            print("\033[94mCodriver\033[0m: See you next time.")
            break

        elif '|?' in command:
            try:
                separator_pos = command.find('|?')
                real_command = command[:separator_pos].strip()
                ai_prompt = command[separator_pos + 2:].strip()
                if not real_command or not ai_prompt:
                    print("\x1b[91mInvalid format. Both a command and a prompt are required.\x1b[0m")
                    continue
                def run_and_capture_inner(cmd):
                    return run_and_capture(cmd)
                print(f"\x1b[90mRunning '{real_command}' and piping output to AI...\x1b[0m")
                os.chdir(current_directory)
                result = run_and_capture_inner(real_command)
                if result.stdout.strip():
                    history.append({"role": "assistant", "content": f"Command output:\n{result.stdout}"})
                if result.stderr.strip():
                    history.append({"role": "assistant", "content": f"Command error:\n{result.stderr}"})
                if result.returncode != 0:
                    error_message = result.stderr if result.stderr else result.stdout
                    print(f"\x1b[91mError executing command:\n{error_message}\x1b[0m")
                    error_fixing_prompt = f"""The user's command `{real_command}` failed with the error:
{error_message}
Provide a corrected command. Reply ONLY with the command."""
                    print("\x1b[90mCalling AI for a suggested fix...\x1b[0m")
                    suggested_command = modellogic.command_openai(error_fixing_prompt, history)
                    if not suggested_command or not suggested_command.strip():
                        print("\x1b[91mCodriver: No suggestion from AI.\x1b[0m")
                        continue
                    confirmation = input(f"\n\033[94mCodriver:\033[0m Run corrected command `{suggested_command}`? (Y/n) ")
                    if confirmation.lower() == 'y':
                        real_command = suggested_command
                        result = run_and_capture_inner(real_command)
                        if result.stdout.strip():
                            history.append({"role": "assistant", "content": f"Command output:\n{result.stdout}"})
                        if result.stderr.strip():
                            history.append({"role": "assistant", "content": f"Command error:\n{result.stderr}"})
                full_ai_prompt = f"""The user ran the command: `{real_command}`
Output:
---
{result.stdout}
---
Question: "{ai_prompt}"
"""
                modellogic.stream_openai(full_ai_prompt, history)
                modellogic.stream_openai(full_ai_prompt, history)
            except Exception as e:
                print(f"Error in pipe-to-AI block: {e}")

        elif command == 'gpt-4.1':
            modellogic.set_model("gpt-4.1")
            modellogic.set_client(OpenAI(api_key=os.environ.get('OPEN_AI_KEY')))
            print(f"\x1b[90mModel set to {modellogic.get_model()}.\x1b[0m")

        elif command == 'llm':
            if is_port_listening(modellogic.lmstudioIP, modellogic.lmstudioPort):
                modellogic.set_model(modellogic.lmstudioModel)
                modellogic.set_client(OpenAI(base_url=f"http://{modellogic.lmstudioIP}:{modellogic.lmstudioPort}/v1", api_key="lm-studio"))
                print(f"\x1b[90mModel set to {modellogic.get_model()}.\x1b[0m")
            else:
                print("\x1b[90mLLM not online.\x1b[0m")

        elif command == 'reset':
            reset_convo_history()
            clear_screen()
            print(banner)
            print("\n\033[94mCodriver:\033[0m OK. Let's start fresh.")

        elif command.endswith(':') and len(command) == 2:
            os.system(command)
            current_directory = command + os.sep

        elif command.startswith('cd'):
            handle_cd_command(command)

        elif command.split() and command.split()[0].lower() in ['ls', 'dir']:
            def _run_capture(cmd):
                if os_type == 'windows':
                    args = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", cmd]
                    shell = False
                else:
                    args = cmd
                    shell = True
                proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=shell)
                try:
                    out, err = proc.communicate(timeout=20)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    out, err = proc.communicate()
                    err += "\nError: Command timed out after 20 seconds."
                return proc.returncode, out, err
            retcode, out, err = _run_capture(command)
            if retcode != 0:
                print(f"\x1b[91mCommand error:\n{err or out}\x1b[0m")
                # Record error in history
                if err.strip():
                    history.append({"role": "assistant", "content": f"Command error:\n{err}"})
                elif out.strip():
                    history.append({"role": "assistant", "content": f"Command output (error code):\n{out}"})
            else:
                print(out.rstrip())
                # Record successful output in history
                if out.strip():
                    history.append({"role": "assistant", "content": f"Command output:\n{out}"})

        elif command.strip().startswith('@'):
            filenames = [word.lstrip('@') for word in command.split() if word.startswith('@')]
            for filename in filenames:
                absolute_path = os.path.abspath(os.path.join(current_directory, filename))
                if not os.path.exists(absolute_path):
                    print(f"\x1b[91mError: File not found at '{absolute_path}'\x1b[0m")
                    continue
                try:
                    if os.path.getsize(absolute_path) > 1 * 1024 * 1024:
                        print(f"\x1b[91mError: File '{filename}' too large.\x1b[0m")
                        continue
                    with open(absolute_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                    history.append({
                        "role": "user",
                        "content": f"Here is the content of the file '{filename}':\n\n---\n{file_content}\n---"
                    })
                    print(f"\x1b[90mAdded '{filename}' to context.\x1b[0m")
                except Exception as e:
                    print(f"\x1b[91Error reading file '{filename}': {e}")

        elif command.startswith('save '):
            filename = command[5:].strip()
            if not filename:
                print("\x1b[91mUsage: save <filename>\x1b[0m")
                continue
            last_response = None
            for msg in reversed(history):
                if msg.get('role') == 'assistant':
                    last_response = msg.get('content')
                    break
            if last_response:
                try:
                    absolute_path = os.path.abspath(os.path.join(current_directory, filename))
                    with open(absolute_path, 'w', encoding='utf-8') as f:
                        f.write(last_response)
                    print(f"\x1b[90mSaved to '{filename}'.\x1b[0m")
                except Exception as e:
                    print(f"\x1b[91Error saving file: {e}\x1b[0m")
            else:
                print("\x1b[91No assistant response to save.\x1b[0m")

        else:
            # Classification logic unchanged
            model_choice = (os.environ.get('classifyingModel') or classifyingModel or "gpt-4.1-nano").strip()
            if model_choice.lower() == "lmstudio":
                if is_port_listening(modellogic.lmstudioIP, modellogic.lmstudioPort):
                    classification_client = OpenAI(base_url=f"http://{modellogic.lmstudioIP}:{modellogic.lmstudioPort}/v1", api_key="lm-studio")
                    model_for_classification = modellogic.lmstudioModel
                else:
                    classification_client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))
                    model_for_classification = "gpt-4.1-nano"
            else:
                classification_client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))
                model_for_classification = model_choice
            classification_system_prompt = {"role": "system", "content": "You are a command classifier. Respond with only QUERY, COMMAND, or SHELL."}
            classification_user_prompt = {"role": "user", "content": f"User input: {command}"}
            try:
                classification_response = classification_client.chat.completions.create(
                    model=model_for_classification,
                    messages=[classification_system_prompt, classification_user_prompt],
                    stream=False
                )
                intent = classification_response.choices[0].message.content.strip().upper()
            except Exception as e:
                print(f"\x1b[91mClassification error: {e}\x1b[0m")
                intent = "SHELL"
            if intent == 'QUERY':
                modellogic.stream_openai(command, history)
            elif intent == 'COMMAND':
                ai_response = modellogic.command_openai(command, history)
                confirmation = input(f"\n\033[94mCodriver:\033[0m Run `{ai_response}`? (Y/n) ")
                if confirmation.lower() in ('y','', 'yes'):
                    print(f"\n\x1b[90mRunning {ai_response}\x1b[0m")
                    # Use the unified execution helper to capture output and errors
                    execute_and_record(ai_response)
            elif intent == 'SHELL':
                execute_and_record(command)
            else:
                print("\x1b[91mUnknown intent, defaulting to SHELL.\x1b[0m")
                execute_and_record(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[94mCodriver:\x1b[0m See you next time.")
    except Exception as e:
        print(f"An error occurred: {e}")
