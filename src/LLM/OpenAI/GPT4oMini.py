from src.LLM.OpenAI.OpenAI import BaseOpenAI

class GPT4oMini(BaseOpenAI):
    def __init__(self, temperature, top_p):
        repo_id: str = "gpt-4o-mini"
        super().__init__(repo_id, temperature, top_p)