"""
This module handles the interaction with the AI models.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get('OPEN_AI_KEY'))
lmstudioIP = os.environ.get('lmstudioIP')
lmstudioPort = os.environ.get('lmstudioPort')
lmstudioModel = os.environ.get('lmstudioModel')
model = os.environ.get('defaultModel')
classifyingModel = os.environ.get('classifyingModel')

def get_client():
    """Returns the current OpenAI client."""
    return client

def set_client(new_client):
    """Sets the OpenAI client."""
    global client
    client = new_client

def get_model():
    """Returns the current model."""
    return model

def set_model(new_model):
    """Sets the model."""
    global model
    model = new_model

def stream_openai(prompt, history):
    
    full_message = ""
    user_response_obj = {"role": "user", "content": prompt}
    history.append(user_response_obj)
    
    response = client.chat.completions.create(model=get_model(), messages=history, stream=True)
    
    print("\n\033[94mCodriver:\x1b[0m", end='')
    for data in response:
        for choice in data.choices:
            if choice.delta and choice.delta.content:
                chunk = choice.delta.content
                print(chunk, end='')
                full_message += chunk
                
    history.append({"role": "assistant", "content": full_message})
    print("\n")
    return full_message

def command_openai(prompt, history):
    
    user_response_obj = {
        "role": "user",
        "content": f"""The user is asking you to run a command that accomplishes the following: {prompt} 
                         -- Since this is a request for YOU to run the command it is VITAL that you reply ONLY with the command. 
                         No codeblock. No comments. ONLY REPLY WITH THE COMMAND SO THAT IT CAN BE SENT STRAIGHT THROUGH TO THE OS AND WORK AS EXPECTED. 
                         If it's not possible to do what the user wants or it's too dangerous, just reply with the suitable COMMAND to print out why to the screen."""
    }
    history.append(user_response_obj)
    
    # Use a non-streaming request for robustness, as we expect a single, complete command.
    response = client.chat.completions.create(model=get_model(), messages=history, stream=False)
    
    # Extract the full message content from the non-streaming response.
    full_message = response.choices[0].message.content
                
    history.append({"role": "assistant", "content": full_message})
    return full_message
