from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from src.config import MAX_GENERATION_TOKEN

class Qwen25_7B_Instruct():
    def __init__(self, temperature=0.7, top_p=0.9):
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        self.temperature = temperature
        self.top_p = top_p
        self.model = None
        self.tokenizer = None

    def prepare_model(self):
        if not self.model or not self.tokenizer:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

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

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=MAX_GENERATION_TOKEN,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id
        )

        # Trim the input tokens from the output tokens
        generated_ids_trimmed = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
        return response

    def step_key(self) -> str:
        return f"{self.model_name}"

    def get_display_name(self) -> str:
        return self.model_name
