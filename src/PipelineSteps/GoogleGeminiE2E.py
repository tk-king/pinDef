from src.Pipeline import PipelineStep

from src.DB import CacheCollection, Component, Pin

from google import genai
from google.genai import types
from langchain_core.output_parsers import JsonOutputParser
from src.config import GOOGLE_API_KEY
from src.config import EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P


class GoogleGeminiE2E(PipelineStep):
    def __init__(self, model, instructions, question):
        super().__init__()
        self.model = model
        self.instructions = instructions
        self.question = question
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    def step_key(self):
        return f"{self.model}_{self.instructions.version}_{self.question.version}"

    def get_display_name(self):
        return f"Google Gemini ({self.model})"

    def invoke(self, component: Component, _: Component) -> list:
        if not component:
            raise ValueError("Component is required")

        # Read PDF bytes
        with open(component.pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # Prepare contents for Gemini model
        contents = [
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf",
            ),
            self.instructions.content,
            self.question.content,
        ]

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=EXTRACTION_LLM_TEMPERATURE,
                top_p=EXTRACTION_LLM_TOP_P,
            ),
        )

        output_parser = JsonOutputParser()
        json_output = output_parser.invoke(response.text)
        pins = [Pin(**x) for x in json_output]
        return [pin.model_dump() for pin in pins]
