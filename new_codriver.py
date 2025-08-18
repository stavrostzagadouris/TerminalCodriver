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
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.styles import Style


import new_modellogic as modellogic

load_dotenv()

# System prompts
windows_prompt = {
    "role": "system",
    "content": "Your name is Codriver. You are a virtual assistant embedded \n                within the Windows Terminal running Powershell, specialized in aiding users with PowerShell \n                and Windows commands that work within Powershell. \n                Your role is to provide accurate and efficient command suggestions, troubleshooting tips, and explanations. \n                You also have the ability to run commands yourself, but only when specifically told to reply\n                with a command.\n                Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. You understand \n                common PowerShell scripts, Windows system commands, and administrative tasks. Keep your \n                responses short if the user only wants to know how to do something. \n                Example: 'how do I list a folders contents?' simply reply with 'dir'"
}

linux_prompt = {
    "role": "system",
    "content": "Your name is Codriver. You are a virtual assistant \n                embedded within the Linux Terminal, specialized in aiding users with Bash commands \n                and Linux system administration. \n                Your role is to provide accurate and efficient command suggestions, troubleshooting tips, and explanations. \n                You also have the ability to run commands yourself, but only when specifically told to reply\n                with a command. Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. You understand \n                common Bash scripts, Linux system commands, and administrative tasks. Keep your \n                responses short if the user only wants to know how to do something. \n                Example: 'how do I list a folders contents?' simply reply with 'dir'"
}

# OS detection
os_type = 'linux' if os.name == 'posix' else 'windows'

# Initialize colorama on Windows to handle ANSI escape codes
if os_type == 'windows':
    try:
        import colorama
        colorama.init()
    except ImportError:
        # Silently fail if colorama is not installed. The lack of colors will be the indicator.
        pass

defaultIdentity = linux_prompt if os_type == 'linux' else windows_prompt
history = [defaultIdentity]

# Welcome banner
banner = f"""
\033[94mCodriver\x1b[0m is now online.
\x1b[90m🤖 Codriver decides your intent automatically.
💬 Type a shell command directly, ask the ai a question, or ask the ai to run a command for you.
⌨️ Pipe your command along with a '?' to ai to ask it about the output. eg. 'dir |? how many files are in here?'
🔁 gpt-5-mini or llm -- Model selection
⬅️ reset - Resets conversation history.
👋 exit -- Quit\x1b[0m
"""

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os_type == 'windows' else 'clear')

def reset_convo_history():
    """Resets the conversation history."""
    global history
    history = [defaultIdentity]

def is_port_listening(ip_address, port):
    """Checks if a port is open."""
    try:
        with socket.create_connection((ip_address, port), timeout=1):
            return True
    except (ConnectionRefusedError, socket.timeout):
        return False

current_directory = os.getcwd()

def handle_cd_command(command):
    """Handles the 'cd' command."""
    global current_directory

    # Pre-process the command to handle 'cd..'
    if command.strip() == 'cd..':
        command = 'cd ..'

    parts = command.split()
    
    if len(parts) == 1:
        # This now only handles 'cd'
        target_directory = os.path.expanduser("~")
    elif len(parts) == 2:
        # This handles 'cd ..', 'cd ~', 'cd /path'
        target_directory = os.path.expanduser(parts[1])
    else:
        # Handles cases like 'cd "my documents"'
        target_directory = os.path.expanduser(" ".join(parts[1:]))

    try:
        os.chdir(target_directory)
        current_directory = os.getcwd()
        # The prompt will show the new directory, no need to print it.
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target_directory}")
    except Exception as e:
        print(f"cd: {e}")

def run_powershell_command(command, directory):
    """Runs a PowerShell command in the specified directory."""
    try:
        os.chdir(directory)
        # By removing check=True, we let PowerShell print its own errors to the console,
        # which feels more natural than Python catching it and printing a traceback.
        subprocess.run(["powershell", "-Command", command])
    except FileNotFoundError:
        print("Error: 'powershell' command not found. Is PowerShell installed and in your PATH?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main application loop."""
    global current_directory
    clear_screen()
    print(banner)

    # Create a PromptSession with a PathCompleter for filenames
    path_completer = PathCompleter()
    
    # Define the style for the prompt components
    style = Style.from_dict({
        'directory': 'ansigray', # to use default terminal color
        'prompt': 'ansicyan',
    })

    session = PromptSession(completer=path_completer, style=style)
    
    while True:
        try:
            # The prompt is now defined as a list of (style_class, text) tuples
            # This lets prompt_toolkit handle all color rendering.
            prompt_char = ">" if os_type == "windows" else "$"
            prompt_message = [
                ('class:directory', f"\n{current_directory}"),
                ('class:prompt', f"{prompt_char} "),
            ]
            command = session.prompt(prompt_message)

        except (EOFError, KeyboardInterrupt):
            print("\n\033[94mCodriver\033[0m: See you next time.")
            break

        if not command.strip():
            continue
            
        if command.lower() in ['exit', 'quit']:
            print("\033[94mCodriver\033[0m: See you next time.")
            break

        # This new block handles the "pipe to AI" feature with intelligent error correction
        elif '|?' in command:
            try:
                # 1. Find the separator and split the string robustly
                separator_pos = command.find('|?')
                real_command = command[:separator_pos].strip()
                ai_prompt = command[separator_pos + 2:].strip()

                # Check if either part is empty after stripping
                if not real_command or not ai_prompt:
                    print("\x1b[91mInvalid format. Both a command and a prompt are required. Use: <command> |? <question>\x1b[0m")
                    continue

                # --- Function to run a command and capture output with a timeout ---
                def run_and_capture(cmd):
                    if os_type == 'windows':
                        args = ["powershell", "-Command", cmd]
                        shell = False
                    else:
                        args = cmd
                        shell = True
                    
                    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=shell)
                    try:
                        stdout, stderr = proc.communicate(timeout=20)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        stdout, stderr = proc.communicate()
                        stderr = stderr + "\nError: Command timed out after 20 seconds."
                    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)
                # ----------------------------------------------------------------

                # 2. Execute the command and capture its output
                print(f"\x1b[90mRunning '{real_command}' and piping output to AI...\x1b[0m")
                os.chdir(current_directory)
                result = run_and_capture(real_command)

                # 3. If the command failed, ask the AI for a fix
                if result.returncode != 0:
                    error_message = result.stderr if result.stderr else result.stdout
                    print(f"\x1b[91mError executing command:\n{error_message}\x1b[0m")
                    
                    error_fixing_prompt = f"""The user's command `{real_command}` failed with the error:
                    {error_message}
                    The user's original intent was to answer the question: "{ai_prompt}"
                    Based on the error, provide a corrected command that will likely work.
                    IMPORTANT: Reply ONLY with the corrected command, without any explanation.
                    """
                    
                    print("\x1b[90mCalling AI for a suggested fix...\x1b[0m")
                    suggested_command = modellogic.command_openai(error_fixing_prompt, history)

                    if not suggested_command or not suggested_command.strip():
                        print("\x1b[91mCodriver: The AI could not suggest a fix. Aborting.\x1b[0m")
                        continue

                    print(f"\n\033[94mCodriver:\033[0m It looks like that command failed. I think this might work instead:")
                    print(f"  \x1b[36m{suggested_command}\x1b[0m")
                    confirmation = input(f"\n\033[94mCodriver:\033[0m Shall I run this corrected command instead? (y/n) ")
                    
                    if confirmation.lower() == 'y':
                        real_command = suggested_command
                        print(f"\x1b[90mRunning corrected command: '{real_command}'...\x1b[0m")
                        result = run_and_capture(real_command)

                        if result.returncode != 0:
                            print(f"\x1b[91mThe corrected command also failed:\n{result.stderr if result.stderr else result.stdout}\x1b[0m")
                            continue
                    else:
                        continue

                # 4. Construct a detailed prompt for the AI with the command's output
                full_ai_prompt = f"""The user ran the command: `{real_command}`
                The output of that command is:
                ---
                {result.stdout}
                ---
                Based on that output, the user is now asking: "{ai_prompt}"
                """
                # 5. Send the combined context to the AI for the final answer
                modellogic.stream_openai(full_ai_prompt, history)

            except Exception as e:
                print(f"An error occurred while handling the pipe to AI: {e}")

        
            
        
            
        elif command == 'gpt-5-mini':
                modellogic.set_model("gpt-5-mini")
                modellogic.set_client(OpenAI(api_key=os.environ.get('OPEN_AI_KEY')))
                print(f"\x1b[90mModel set to {modellogic.get_model()}.\x1b[0m")
            
        elif command == 'llm':
                if is_port_listening(modellogic.lmstudioIP, modellogic.lmstudioPort):
                    modellogic.set_model(modellogic.lmstudioModel)
                    modellogic.set_client(OpenAI(base_url=f"http://{modellogic.lmstudioIP}:{modellogic.lmstudioPort}/v1", api_key="lm-studio"))
                    print(f"\x1b[90mModel set to {modellogic.get_model()}.\x1b[0m")
                else:
                    print(f"\x1b[90mLLM not online. Model remains {modellogic.get_model()}.\x1b[0m")
                
        elif command == 'reset':
                    reset_convo_history()
                    clear_screen()
                    print(banner)
                    print(f"\n\033[94mCodriver:\033[0m OK. Let's start fresh.")
            
        elif command.endswith(':') and len(command) == 2:
                os.system(command)
                current_directory = command + os.sep
            
        elif command.startswith('cd'):
                handle_cd_command(command)
            
        else: # New AI classification logic
            # Initialize a temporary OpenAI client for classification
            # Using gpt-5-nano 
            # This call does not affect the main conversation history.
            classification_client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))
            
            classification_system_prompt = {
                "role": "system",
                "content": "You are a command classifier. Your task is to analyze user input and determine its intent. Respond with only one of the following words: 'QUERY' if the user is asking a question or talking to an AI, 'COMMAND' if the user wants an AI to generate and run a command, or 'SHELL' if the user is directly typing a shell command. Do not include any other text or explanation."
            }
            
            classification_user_prompt = {
                "role": "user",
                "content": f"User input: {command}"
            }
            
            try:
                classification_response = classification_client.chat.completions.create(
                    model="gpt-5-nano", # Using gpt-5-nano for classification
                    messages=[classification_system_prompt, classification_user_prompt],
                    stream=False
                )
                intent = classification_response.choices[0].message.content.strip().upper()
            except Exception as e:
                print(f"\x1b[91mCodriver: Error classifying command with AI: {e}. Defaulting to shell execution.\x1b[0m")
                intent = "SHELL" # Default to shell if classification fails

            if intent == 'QUERY':
                ai_prompt = command.strip() # No need to remove '?' as it's now a classified query
                modellogic.stream_openai(ai_prompt, history)
            elif intent == 'COMMAND':
                ai_prompt = command.strip() # No need to remove '!' as it's now a classified command request
                ai_response = modellogic.command_openai(ai_prompt, history)
                print(f"\n\033[94mCodriver:\033[0m I would like to run this command: {ai_response}")
                confirmation = input(f"\n\033[94mCodriver:\033[0m May I? (y/n)")
                if confirmation.lower() == 'y':   
                    print(f"\n\033[94mCodriver:\033[0m Running {ai_response}")
                    if os_type == 'windows':
                        run_powershell_command(ai_response, current_directory)
                    else:
                        os.chdir(current_directory)
                        os.system(ai_response)
            elif intent == 'SHELL':
                # For any other command, execute it directly.
                if os_type == 'windows':
                    run_powershell_command(command, current_directory)
                else:
                    os.chdir(current_directory)
                    os.system(command)
            else:
                print(f"\x1b[91mCodriver: Unrecognized AI classification '{intent}'. Defaulting to shell execution.\x1b[0m")
                if os_type == 'windows':
                    run_powershell_command(command, current_directory)
                else:
                    os.chdir(current_directory)
                    os.system(command)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[94mCodriver:\x1b[0m See you next time.")
    except Exception as e:
        print(f"An error occurred: {e}")