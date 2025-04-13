from openai import OpenAI
import re
import os

# https://www.anthropic.com/engineering/building-effective-agents

def llm_call(prompt: str, system_prompt: str = 'Answer in Chinese', model: str = 'qwen-plus') -> str:
    """
    Call the model with the given prompt and returns the response.

    Args:
        prompt (str): The user prompt to send to the model.
        system_prompt (str, optinal): The system prompt to send to the model. Defaults to "".
        model (str, optinal): The model to use.

    Returns:
        str: The response from the model.
    """

    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    messages = []
    if system_prompt != '':
        messages.append({'role':'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    completion = client.chat.completions.create(
    model=model,
    messages=messages,
    )
    
    return completion.choices[0].message.content

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""