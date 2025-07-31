import os
import json
from openai import OpenAI
from functools import wraps

def retry_json_decode(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(self, messages, model="gpt-4.1", requires_json=False):
            if not requires_json:
                return func(self, messages, model, requires_json)
            
            for attempt in range(max_retries):
                try:
                    return func(self, messages, model, requires_json)
                except json.JSONDecodeError:
                    if attempt == max_retries - 1:
                        return []
                    continue
            
        return wrapper
    return decorator

class LLM:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @retry_json_decode()
    def prompt(self, messages, model = "gpt-4.1", requires_json = False):
        response = self.client.responses.create(
            model=model,
            input=messages
        )
        response = response.output_text
        if requires_json:
            response = json.loads(response)
        return response
    
    def prompt_stream(self, messages, model = "gpt-4.1"):
        response = self.client.responses.create(
            model=model,
            input=messages,
            stream=True
        )
        for event in response:
            # Listen for text delta events to get streaming content
            if event.type == "response.output_text.delta":
                yield event.delta