from src.Pipeline.PipelineStep import PipelineStep
from src.llm_inputs import VersionComponent
from src.DB.Component import Component, Pin
from src.Utils.MergePins import merge_pins, MergedPin
from pydantic import validate_call
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from pydantic import BaseModel


class GraderResult(BaseModel):
    name: bool
    description: bool

class LLMGrader(PipelineStep):
    def __init__(self, llm, grading_instructions : VersionComponent):
        super().__init__()
        self.llm = llm
        self.grading_instructions = grading_instructions

    def step_key(self):
        return self.llm.step_key() + "_" + self.grading_instructions.version
    
    def get_display_name(self):
        return f"LLMGrader ({self.llm.get_display_name()})"

    def _run_llm(self, pin : MergedPin):
            question = f"""
                    This is the ground truth:
                    {{
                    "name": "{pin.human_pin.name}",
                    "description": "{pin.human_pin.description}"
                    }}

                    This is the generated data:
                    {{
                    "name": "{pin.llm_pins.name}",
                    "description": "{pin.llm_pins.description}"
                    }}
                """
            out = self.llm.invoke(question=question, instructions=self.grading_instructions.content)
            output_parser = JsonOutputParser(pydantic_object=GraderResult)
            assert isinstance(out, str), f"LLM output is not a string: {out}"
            json_output = output_parser.invoke(out)
            return json_output


    @validate_call
    def invoke(self, input : List[Pin], component : Component):
        merged_pins : List[MergedPin] = merge_pins(component, input)
        for i, pin in enumerate(merged_pins):
            if pin.llm_pins is None or pin.human_pin is None:
                continue
            json_output = self._run_llm(pin)
            merged_pins[i].name_correct = json_output.get("name", None)
            merged_pins[i].description_correct = json_output.get("description", None)
        return merged_pins