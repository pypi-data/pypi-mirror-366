import os
import numpy as np
import subprocess
import tempfile
import requests
from .prompts import agent_prompt, answer_prompt, summary_prompt, compact_prompt
from ..llm import LLM


class Agent:
    def __init__(self, api_key=None):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_key = api_key
        self.last_usage = 0
        self.last_limit = 0
        
    def parse_messages(self, messages: list) -> list:
         parsed_messages = []
         for message in messages:
             if isinstance(message, dict) and "role" in message and "content" in message:
                 parsed_messages.append({
                     "role": message["role"],
                     "content": message["content"]
                 })
         return parsed_messages

    def run(self, messages: str) -> str:
        message = []
        message.append({"role": "developer", "content": agent_prompt})
        message.extend(self.parse_messages(messages))
        response = LLM().prompt(message, requires_json = True)
        return response
    
    def action(self, question, title, description):
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "question": question,
                "title": title,
                "description": description
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                "https://rallies.ai/api/complete-cli-action",
                json=payload,
                headers=headers,
                timeout=180
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("allowed") == False:
                    error_msg = result.get("error", "Unknown error")
                    if "Rate limit exceeded" in error_msg:
                        error_display = f"[red]⚠ Rate limit reached:[/red] {error_msg}"
                    elif "Invalid API key" in error_msg:
                        error_display = f"[red]⚠ Authentication failed:[/red] Invalid API key"
                    else:
                        error_display = f"[red]⚠ Access denied:[/red] {error_msg}"
                    raise Exception(error_display)
                
                self.last_usage = result.get("current_usage", 0)
                self.last_limit = result.get("limit", 0)
                return result.get("results", "No results returned")
            else:
                raise Exception(f"[red]⚠ API Error:[/red] Request failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"[red]⚠ Network Error:[/red] {str(e)}")
        except Exception as e:
            if "[red]" in str(e):
                raise
            raise Exception(f"[red]⚠ Error:[/red] {str(e)}")
    
    def summarize(self, messages):
        message = []
        message.append({"role": "developer", "content": summary_prompt})
        message.extend(self.parse_messages(messages))
        summary = LLM().prompt(message)
        return summary
    
    def answer(self, question, messages):
        message = []
        answer_prompt_formatted = answer_prompt.replace("--question--", question)
        message.append({"role": "developer", "content": answer_prompt_formatted})
        message.extend(self.parse_messages(messages))
        for chunk in LLM().prompt_stream(message):
            yield chunk

    def compact(self, messages):
        message = []
        message.append({"role": "developer", "content": compact_prompt})
        message.extend(self.parse_messages(messages))
        summary = LLM().prompt(message)

        messages.clear()
        messages.append({"role": "user", "content": summary})
        return messages