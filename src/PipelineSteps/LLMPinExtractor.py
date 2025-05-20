from src.Pipeline import PipelineStep
from src.DB import Component, Pin
from langchain_core.output_parsers import JsonOutputParser
from src.llm_inputs import VersionComponent


class LLMPinExtractor(PipelineStep):
    def __init__(self, llm, llm_question: VersionComponent, llm_instructions: VersionComponent, llmOrVLM="llm"):
        super().__init__()
        self.llm = llm
        self.llmOrVLM = llmOrVLM
        assert llmOrVLM in ["llm", "vlm"], f"Invalid llmOrVLM: {llmOrVLM}"
        self.llm_question = llm_question
        self.llm_instructions = llm_instructions

    def step_key(self):
        return f"{self.llm.step_key()}_{self.llm_question.version}_{self.llm_instructions.version}"
    
    def get_display_name(self):
        return f"PinExtractor ({self.llm.get_display_name()})"

    def offload_resources(self):
        if hasattr(self.llm, "model") and self.llm.model is not None:
            del self.llm.model
            self.llm.model = None
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def invoke(self, input, c: Component):
        text_context = "\n".join(rag_texts["text"] for rag_texts in input)
        page_context = [rag_texts["page"] for rag_texts in input]
        context = text_context if self.llmOrVLM == "llm" else page_context
        raw_output = None
        if self.llmOrVLM == "llm":
            raw_output = self.llm.invoke(question=self.llm_question.content, instructions=self.llm_instructions.content, context=context)
        else:
            raw_output = self.llm.invoke(question=self.llm_question.content, instructions=self.llm_instructions.content, context=context, component=c)
        output_parser = JsonOutputParser()
        json_output = output_parser.invoke(raw_output)
        output = []
        for x in json_output or []:
            output.append(Pin(**x).model_dump())
        return output
