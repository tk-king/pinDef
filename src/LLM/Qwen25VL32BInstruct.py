from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from src.Utils.Image import pdf_pages_to_base64
from src.DB.Component import Component
from src.config import MAX_GENERATION_TOKEN

import torch


class Qwen25_VL_32B_Instruct():
    def __init__(self, temperature, top_p):
        self.model_name = "Qwen/Qwen2.5-VL-32B-Instruct"
        self.temperature = temperature
        self.top_p = top_p
        self.model = None
        self.processor = None
        self.eos_token_id = None

    def prepare_model(self):
        if not self.model or not self.processor:
            min_pixels = 256 * 28 * 28
            max_pixels = 1280 * 28 * 28
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                 "Qwen/Qwen2.5-VL-32B-Instruct",
                 torch_dtype=torch.bfloat16,
                 attn_implementation="flash_attention_2",
                 device_map="auto",
            )
            
            # default processor
            self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-32B-Instruct")
            self.eos_token_id = self.processor.tokenizer.eos_token_id

    def invoke(self, question, instructions, context, component: Component):
        self.prepare_model()

        images = pdf_pages_to_base64(component.pdf_path, context)

        # Merge images and question into one user message
        image_content = [{"type": "image", "image": "data:image;base64," + image} for image in images]
        image_content.append({"type": "text", "text": question})

        messages = [
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": image_content
            }
        ]

        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        inputs = inputs.to("cuda")

        generated_ids = self.model.generate(
            **inputs,
            max_new_tokens=MAX_GENERATION_TOKEN,
            eos_token_id=self.eos_token_id,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True
        )

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        return output_text[0]

    def step_key(self) -> str:
        return f"{self.model_name}"

    def get_display_name(self) -> str:
        return self.model_name
