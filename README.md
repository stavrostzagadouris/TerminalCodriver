# TerminalCodriver
Windows or Linux -- OpenAI or LM-Studio right in your terminal with you. All commands are just sent straight through to your terminal, however you have the option to ask AI a question right in the terminal by prepending your command with a '?'.

## Features

- **Dynamically detects** whether you're using Linux or Windows.
- **Passes normal commands** straight through to your OS.
- **Chat functionality**: Start any command with `?` to chat and get quick answers to your queries.
- **Auto command running**: Start any command with `!` and your codriver will tell you the command it's going to run AND just run it for you (be careful with this) eg. !how much space do I have left on my C drive? -- It will just run Get-PSDrive C:

## Installation

To get started with TerminalCodriver, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jiberwabish/TerminalCodriver.git
Navigate to the project directory:

cd TerminalCodriver
Install dependencies: Make sure you have Python installed on your system. Then, install required libraries using pip:

pip install -r requirements.txt

Create your own .env file based on the example and enter at least an openai api key. Everything else is optional.

Usage
To run TerminalCodriver, simply execute the following command in your terminal:

python codriver.py

Command Passing
You can type any command normally, and it will be executed in your terminal.

Chat Feature
To ask a question, prefix your command with ?. For example:

? how do I create a new firewall rule? I forget.
This will initiate a chat and provide you with an answer directly in your terminal.
