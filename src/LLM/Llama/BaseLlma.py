import torch
from transformers.models.llama.modeling_llama import LlamaForCausalLM
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast

from src.Utils.PromptTemplate import PromptTemplate
from src.config import MAX_GENERATION_TOKEN


class LlamaBase():

    def __init__(self, repo_id: str, temperature, top_p):
        self.repo_id = repo_id
        self.temperature = temperature
        self.top_p = top_p

        self.model = None
        self.tokenizer = None

        prompt_template = """
                <|begin_of_text|><|start_header_id|>system<|end_header_id|>
                {{instructions}}<|eot_id|>
                <|start_header_id|>user<|end_header_id|>
                {{question}}<|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>
            """
        self.prompt_template = PromptTemplate.from_string(prompt_template)

    def prepare_model(self):
        if self.model is None or self.tokenizer is None:
            self.model = LlamaForCausalLM.from_pretrained(
                self.repo_id,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            self.tokenizer = PreTrainedTokenizerFast.from_pretrained(self.repo_id)

    def invoke(self, question, instructions, context=""):
        self.prepare_model()

        prompt = self.prompt_template.invoke(question=question + context, instructions=instructions)
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.model.device)

        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.model.generate(
            input_ids,
            max_new_tokens=MAX_GENERATION_TOKEN,
            # eos_token_id=terminators,
            do_sample=True,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        response = outputs[0][input_ids.shape[-1]:]
        output = self.tokenizer.decode(response, skip_special_tokens=True)
        output = output.split("<|start_header_id|>assistant<|end_header_id|>")
        return output[-1]
