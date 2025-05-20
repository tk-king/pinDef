from src.Pipeline import PipelineStep

from src.DB import CacheCollection, Component, Pin
from langchain_core.output_parsers import JsonOutputParser

import openai



class OpenAIE2E(PipelineStep):
    def __init__(self, model, instructions, question):
        super().__init__()
        self.model = model
        self.instructions = instructions
        self.question = question
        self.client = openai.OpenAI()

    def step_key(self):
        return f"{self.model}_{self.instructions.version}_{self.question.version}"       

    def get_display_name(self):
        return f"OpenAI ({self.model})"

    def invoke(self, component: Component, _: Component) -> list:
        if not component:
            raise ValueError("Component is required")
        
        
        file = self.client.files.create(
            file=open(component.pdf_path, "rb"),
            purpose="user_data"
        )
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                 {
                      "role": "developer",
                      "content": [{
                           "type": "text",
                            "text": self.instructions.content,
                      }]
                 },
                {
                    "role": "user",
                    "content": [
                        {   
                            "type": "file",
                            "file": {
                                "file_id": file.id,
                            }
                        },
                        {
                            "type": "text",
                            "text": self.question.content,
                        },
                    ]
                }
            ]
        )
        response = completion.choices[0].message.content
    
        output_parser = JsonOutputParser()
        json_output = output_parser.invoke(response)
        pins = [Pin(**x) for x in json_output]
        return [pin.model_dump() for pin in pins]