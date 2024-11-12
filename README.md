## Latest updates
Nov 11, 2024 - Stavros
- updated readme
- added 'reset' command to reset ai conversation history if need be
- cleaned up code a bit and instructions for bot

Nov 10, 2024 - Stavros
- added autoexecution mode, you just say what you want and it crafts and runs the command for you
eg. !how much space is left on my C drive?




# TerminalCodriver
Windows or Linux -- OpenAI or LM-Studio right in your terminal with you. All commands are just sent straight through to your terminal, however you have the option to ask AI a question right in the terminal by prepending your command with a '?'. 

You may also just tell the codriver what you want and it will do it by prepending '!'
   ```bash
   c:\>!tell me how much space is left on my C drive
   Codriver: Running Get-PSDrive C:

   Name           Used (GB)     Free (GB) Provider      Root
                                                            
                                                            
                                                            
   ----           ---------     --------- --------      ----
   C                 559.04        371.72 FileSystem    C:\ 
   ```


## Features

- **Dynamically detects** whether you're using Linux or Windows.
- **Passes normal commands** straight through to your OS.
- **Chat functionality**: Start any command with `?` to chat and get quick answers to your queries.
- **Auto command running**: Start any command with `!` and your codriver will tell you the command it's going to run AND just run it for you (be careful with this) eg. !how much space do I have left on my C drive? -- It will just run Get-PSDrive C:
- **Maintains history of your conversation**: History is kept, so you don't need to remind it about what you're currently doing. The exception here is if you use the '!' command, it will wipe after every execution. Otherwise it will get confused and reply with commands when you're actually trying to talk to it.

## Installation

To get started with TerminalCodriver, follow these steps:

**Clone the repository:**

```bash
git clone https://github.com/jiberwabish/TerminalCodriver.git
```

**Navigate to the project directory:**

```bash
cd TerminalCodriver
```

**Install dependencies:**

Make sure you have Python installed on your system. Then, install required libraries using pip:

```bash
pip install -r requirements.txt
```

Create your own .env file based on the example and enter at least an openai api key. Everything else is optional.

**Usage**
To run TerminalCodriver, simply execute the following command in your terminal:

```bash
python codriver.py
```

**Command Passing**
You can type any command normally, and it will be executed in your terminal.

**Chat Feature**
To ask a question, prefix your command with ?. For example:

```bash
? how do I create a new firewall rule? I forget.
```
This will initiate a chat and provide you with an answer directly in your terminal.

As shown above, you can have it run commands for you without running them by you:
```bash
c:\>!tell me how much space is left on my C drive
Codriver: Running Get-PSDrive C:

Name           Used (GB)     Free (GB) Provider      Root
                                                         
                                                         
                                                         
----           ---------     --------- --------      ----
C                 559.04        371.72 FileSystem    C:\ 
```

