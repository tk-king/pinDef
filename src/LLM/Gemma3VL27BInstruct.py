from transformers import AutoProcessor, Gemma3ForConditionalGeneration
from src.Utils.Image import pdf_pages_to_base64
from src.DB.Component import Component
from src.config import MAX_GENERATION_TOKEN

import torch


class Gemma3_VL_27B_Instruct():
    def __init__(self, temperature, top_p):
        self.model_name = "google/gemma-3-27b-it"
        self.temperature = temperature
        self.top_p = top_p
        self.model = None
        self.processor = None
        self.eos_token_id = None

    def prepare_model(self):
        if not self.model or not self.processor:
            self.model = Gemma3ForConditionalGeneration.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.bfloat16
            ).eval()

            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.eos_token_id = self.processor.tokenizer.eos_token_id if hasattr(self.processor, 'tokenizer') else None

    def invoke(self, question, instructions, context, component: Component):
        self.prepare_model()

        images = pdf_pages_to_base64(component.pdf_path, context, output_format="PIL")

        # Merge images and question into one user message
        image_content = [{"type": "image", "image": image} for image in images]
        image_content.append({"type": "text", "text": question})

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": instructions}]
            },
            {
                "role": "user",
                "content": image_content
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt"
        ).to(self.model.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]

        with torch.inference_mode():
            generation = self.model.generate(
                **inputs,
                max_new_tokens=MAX_GENERATION_TOKEN,
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            generation = generation[0][input_len:]

        output_text = self.processor.decode(generation, skip_special_tokens=True)

        return output_text

    def step_key(self) -> str:
        return f"{self.model_name}"

    def get_display_name(self) -> str:
        return self.model_name
