# TerminalCodriver

## Your AI-Powered Command Line Companion

Work in powershell or bash with a codriver at your side.
Auto-intent discovery allows you to just type either commands or questions or requests of the ai and it will handle it.
Treat it like a normal terminal, but ask for ai help when you want.

## Features

*   **Intelligent Command Classification**: Simply type your command, question, or request. The Codriver intelligently determines whether to execute it as a shell command, answer it as a query, or generate and run a command for you.
*   **Seamless Shell Integration**: Pass normal shell commands directly through to your operating system.
*   **AI Chat Functionality**: Ask the AI questions directly within your terminal for quick answers and explanations.
*   **Auto Command Execution**: Describe what you want to achieve, and the Codriver will craft and execute the appropriate command for you (with your confirmation).
*   **Pipe Command Output to AI**: Use the `|?` syntax to pipe the output of any shell command directly to the AI for analysis, summarization, or to ask follow-up questions based on the output. The Codriver can even suggest fixes for failed commands.
*   **Flexible AI Model Support**: Easily switch between different AI models:
    *   Type `gpt-5-mini` to use the OpenAI `gpt-5-mini` model (requires OpenAI API key).
    *   Type `llm` to connect to a local LM Studio instance (requires LM Studio to be running and configured).
    *   Configure these details in the .env
*   **Conversation History**: The Codriver maintains a history of your conversation, allowing for context-aware interactions.
*   **Reset Conversation**: Clear the current conversation history at any time by typing `reset`.
*   **Enhanced Tab Completion**: Enjoy improved tab completion for shell commands, making your input faster and more accurate. (more like tab selection actually...)
*   **Cross-Platform Compatibility**: Dynamically detects and adapts to your operating system (Windows or Linux).

## Installation

To get started with TerminalCodriver, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/stavrostzagadouris/TerminalCodriver.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd TerminalCodriver
    ```
3.  **Install dependencies:**
    Make sure you have Python installed on your system. Then, install required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (.env file)

Create a `.env` file in the root of your project directory based on the `example.env` file. At a minimum, you need to provide your OpenAI API key.

```
# example.env content
OPEN_AI_KEY="your_openai_api_key_here"

# Optional: For LM Studio integration
# lmstudioIP="127.0.0.1"
# lmstudioPort="1234"
# lmstudioModel="your-lm-studio-model-name"

# Optional: Default model to use at startup
# defaultModel="gpt-5-mini"

# Optional: Model for classifying user intent (e.g., a smaller, faster model)
# classifyingModel="gpt-5-nano"
```

**Key variables:**

*   `OPEN_AI_KEY`: Your API key for OpenAI services.
*   `lmstudioIP`: (Optional) The IP address where your LM Studio instance is running.
*   `lmstudioPort`: (Optional) The port your LM Studio instance is listening on.
*   `lmstudioModel`: (Optional) The name of the model loaded in your LM Studio instance.
*   `defaultModel`: (Optional) Specifies the AI model to use by default when the Codriver starts.
*   `classifyingModel`: (Optional) A dedicated model for classifying user input intent (e.g., `gpt-5-nano` for faster classification).

## Usage

To run TerminalCodriver, simply execute the following command in your terminal:

```bash
python codriver.py
```

Once running, you can interact with the Codriver in several ways:

### Running Shell Commands

Type any standard shell command, and the Codriver will execute it directly:

```bash
ls -l
```

### Chatting with AI

Ask the Codriver a question, and it will provide an answer:

```bash
how do I list all running processes on Linux?
```

### Auto Command Execution

Tell the Codriver what you want to achieve, and it will suggest and run the appropriate command (after your confirmation):

```bash
tell me how much space is left on my C drive
```
The Codriver will respond:
```
Codriver: I would like to run this command:

 Get-PSDrive C:

May I? y/n
```
If you type `y` and press Enter, the command will be executed.

### Piping Command Output to AI

Analyze the output of a command or ask a follow-up question based on it using the `|?` syntax:

```bash
dir |? how many files are in here?
```
The Codriver will run `dir`, capture its output, and then send both the command and its output to the AI along with your question. If the initial command fails, the AI will attempt to suggest a fix.

### Switching AI Models

*   To use the OpenAI `gpt-5-mini` model:
    ```bash
    gpt-5-mini
    ```
*   To connect to your local LM Studio instance:
    ```bash
    llm
    ```

### Resetting Conversation History

To clear the current conversation context:

```bash
reset
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.
