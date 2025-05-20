from src.LLM.Llama.BaseLlma import LlamaBase



class Llama31_8B(LlamaBase):
    def __init__(self, temperature, top_p):
        repo_id: str = "meta-llama/Llama-3.1-8B-Instruct"
        super().__init__(repo_id, temperature, top_p)

    @classmethod
    def get_name(cls) -> str:
        return "Llama3.1-8B-Instruct"

    def step_key(self) -> str:
        return f"Llama3.1-8B-Instruct_{self.temperature}_{self.top_p}"
    
    def get_display_name(self) -> str:
        return "Llama-3.1-8B-Instruct"