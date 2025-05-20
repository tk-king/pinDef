
from openai import OpenAI
import os

class BaseOpenAI():
    def __init__(self, model_name, temperature, top_p):
        self.client = None
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p

    def prepare_model(self):
        if self.client is None:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def invoke(self, question, instructions, context=""):
        self.prepare_model()
        messages = [
                {
                    "role": "system",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": question + context
                }
            ]

        response = self.client.chat.completions.create(
            temperature=self.temperature,
            top_p=self.top_p,
            model = self.model_name,
            messages=messages,
        )
        output = response.choices[0].message.content
        return output
        

    def step_key(self) -> str:
        return f"{self.model_name}_{self.temperature}_{self.top_p}"
    
    def get_display_name(self) -> str:
        return self.model_name
