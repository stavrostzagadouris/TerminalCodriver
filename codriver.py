# jiberwabish 2024 - Codriver
# host on your own computer
# Windows or Linux
# when working in the terminal, run this first
# it will feed all commands through to the terminal like normal
# UNLESS your command starts with '?'
# in which case AI will step in and answer your question
# example: ?how do I make a firewall rule to block all access to 8080

import time, os, socket, subprocess
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() #pull .env variables in

client = OpenAI(api_key=os.environ['OPEN_AI_KEY'])
lmstudioIP = os.environ['lmstudioIP']
lmstudioPort = os.environ['lmstudioPort']
lmstudioModel = os.environ['lmstudioModel']

#variable I use as a pre-prompt to provide the bot direction based on the terminal it's in
windows = {"role": "system", "content": "Your name is Codriver. You are a virtual assistant embedded within the Windows Terminal running Powershell, specialized in aiding users with PowerShell and Windows commands that work within Powershell. Your role is to provide accurate and efficient command suggestions, troubleshooting tips, and explanations. Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. You understand common PowerShell scripts, Windows system commands, and administrative tasks. Keep your responses short if the user only wants to know how to do something. Example 'how do I list a folders contents?' simply reply with 'dir'"}
linux = {"role": "system", "content": "Your name is Codriver. You are a virtual assistant embedded within the Linux Terminal, specialized in aiding users with Bash commands and Linux system administration. Your role is to provide accurate and efficient command suggestions, troubleshooting tips, and explanations. Your tone is professional yet approachable, ensuring users feel comfortable seeking your assistance. You understand common Bash scripts, Linux system commands, and administrative tasks. Keep your responses short if the user only wants to know how to do something. Example 'how do I list a folders contents?' simply reply with 'dir'"}

#logic to set bot terminal mode
os_type = 'linux' if os.name == 'posix' else 'windows'
if os_type == 'linux':
    defaultIdentity = linux
else:
    defaultIdentity = windows

history = [defaultIdentity] #fill history with identity to start the conversation
costing = "placeholder"
model = os.environ['defaultModel'] #set this in your .env
modelTemp = 0.8

#welcome message
banner = f"\n\033[94mCodriver\x1b[0m is now online.\n\x1b[90m💬 Start your command with ? if you want to query the AI for help.\n⌨️ Otherwise just work in the terminal as normal and all code is passed through.\n🔁 !gpt4 or !llm -- Model selection\n👋 !exit -- Quit\x1b[0m"

#clear screen
if os_type == 'linux':
    os.system('clear')
else:
    os.system('cls')

# print the pre-defined banner at the top of the terminal
print(banner)

def stream_openai(prompt, history):
    global num_tokens, prompt_token_count, model
    fullMessage = ""
    user_response_obj = {"role": "user", "content": prompt}

    history.append(user_response_obj)
    
    # Send the first message that will continually be edited
    response = client.chat.completions.create(model=model, messages=history, temperature=modelTemp, stream=True)

    print("\n\033[94mCodriver:\x1b[0m", end='')
    fullMessage = ""

    for data in response:
        for choice in data.choices:
            # Check if 'choice.delta.content' exists and is not None
            if choice.delta and choice.delta.content:
                chunk = choice.delta.content
                # Using end='' to avoid adding a new line after each print
                print(chunk, end='')
                fullMessage += chunk
    history.append({"role": "assistant", "content": fullMessage})
    #return fullMessage

def resetConvoHistory():
    global history, defaultIdentity
    history = [defaultIdentity]
    return

#check for llm availability
def is_port_listening(ip_address, port):
    try:
        s = socket.create_connection((ip_address, port), timeout=1)
        s.close()
        return True
    except ConnectionRefusedError:
        return False
    except socket.timeout:
        return False

#needed for keeping track of dir we're in
current_directory = os.getcwd()


def handle_cd_command(command):
    global current_directory
    # Split the command to get the target directory
    parts = command.split()
    
    # If only 'cd' is entered, switch to the user's home directory
    if len(parts) == 1:
        target_directory = os.path.expanduser("~")
    elif len(parts) == 2:
        target_directory = parts[1]
    else:
        print("Invalid cd command format.")
        return

    # Attempt to change to the target directory
    try:
        os.chdir(target_directory)
        current_directory = os.getcwd()  # Update the current directory
        print(current_directory)  # Print the new directory as confirmation
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target_directory}")
    except Exception as e:
        print(f"cd: {e}")

# MODIFY: Function to execute PowerShell commands with proper path context
def run_powershell_command_with_directory(command, directory):
    # Combine changing directory with the actual command using semicolon
    full_command = f"cd '{directory}'; {command}"
    
    # Use the subprocess.run method to execute the command in PowerShell
    result = subprocess.run(["powershell", "-Command", full_command], capture_output=True, text=True)
    
    # Check for errors and print the output
    if result.returncode == 0:
        print(f"{result.stdout}", end='')
    else:
        print("Error:\n", result.stderr)

# MODIFY: Main loop utilizes updated PowerShell function
def main():
    command_history = []
    global current_directory, client  # Ensure we modify the global variable
    
    while True:
        print("\n")
        
        # Display the current directory
        if os_type == "windows":
            command = input(f"{current_directory}\033[36m>\033[0m ")
        else:
            command = input(f"{current_directory}\033[36m$\033[0m ")
        
        # Exit on specific command
        if command.lower() in ['!exit', '!quit']:
            print("\033[94mCodriver\x1b[0m: See you next time.")
            break
        
        # Check if the command is a request for AI assistance
        elif command.startswith('?'):
            ai_prompt = command[1:].strip()
            ai_response = stream_openai(ai_prompt,history)
            resetConvoHistory()

            command_history.append(command)
        elif command == '!gpt4':
            model = "gpt-4o-mini"
            client = OpenAI(api_key=os.environ['OPEN_AI_KEY'])
            print(f"\x1b[90mModel set to {model}.\x1b[0m")
            continue
        elif command == '!llm':
            if is_port_listening(lmstudioIP, lmstudioPort):
                model = lmstudioModel
                client = OpenAI(base_url="http://192.168.64.123:1234/v1", api_key="lm-studio")
                print(f"\x1b[90mModel set to {model}.\x1b[0m")
            else:
                print(f"\x1b[90mLLM not online. Model remains {model}.\x1b[0m")
        
        # Handle 'cd' commands
        # Check if the command is a drive change (like 'D:')
        elif command.endswith(':') and len(command) == 2:
            # Directly change to the specified drive
            os.system(f"{command}")
            current_directory = command + "\\"  # Update for display
        elif command.startswith('cd'):
            handle_cd_command(command)
        
        else:
            # Execute the command with the updated current working directory
            try:
                if os_type == 'windows':
                    run_powershell_command_with_directory(command, current_directory)
                else:
                    os.chdir(current_directory)  # Ensure we're in the right directory on Linux
                    os.system(command)
            except Exception as e:
                print(f"An error occurred while executing command: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[94mCodriver:\x1b[0m See you next time.")
    except Exception as e:
        print(f"An error occurred: {e}")