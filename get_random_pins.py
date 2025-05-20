import asyncio
import random
import json

from typing import List

from src.DB.Component import Component
from src.Utils.MergePins import MergedPin
from src.Pipeline import Pipeline
from src.PipelineSteps import FullPageExtractor, TextRag, LLMPinExtractor, LLMGrader
from src.LLM import Qwen25_VL_7B_Instruct, GPT4oMini
from src.llm_inputs import RAG_QUERY_V1, LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, GRADING_INSTRUCTIONS_V1
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.config import EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P, GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P

async def get_grading_docs():
    pipeline = Pipeline(pipeline_type="vision", save_results=False)
    pipeline.add_step(FullPageExtractor(), exception_policy=ExceptionPolicy.TRY)
    pipeline.add_step(TextRag(RAG_QUERY_V1, num_results=4))
    pipeline.add_step([
        LLMPinExtractor(Qwen25_VL_7B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, llmOrVLM="vlm"),
        ], exception_policy=ExceptionPolicy.TRY, execution_policy=ExecutionPolicy.CACHE_ONLY)
    pipeline.add_step(LLMGrader(GPT4oMini(GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P), GRADING_INSTRUCTIONS_V1))
    
    components = await Component.find().to_list()
    components = [x for x in components if "sensor" in x.type.lower()]
    
    gradings, output = await pipeline(components, execution_policy=ExecutionPolicy.CACHE_ONLY)

    return gradings, output

async def main():
    step_key = "LLMGrader"
    # docs = await CacheCollection.find({"step_key": {"$regex": f"^{step_key}"}}).to_list()
    _, docs = await get_grading_docs()
    docs = docs[0]
    print(f"Found {len(docs)} documents with step_key '{step_key}':")
    merged_pins : List[MergedPin] = []
    for doc in docs:
        doc = doc[0]
        if doc is None:
            continue
        for pin in doc.value:
            merged_pins.append(MergedPin(**pin))
    merged_pins = [pin for pin in merged_pins if pin.llm_pins is not None and pin.human_pin is not None]
    print(f"Found {len(merged_pins)} merged pins with step_key '{step_key}':")
    
    # Select randomly 100 pins
    random_pins = random.sample(merged_pins, min(100, len(merged_pins)))
    # Write to file
    with open("random_pins.json", "w") as f:
        json.dump([pin.model_dump() for pin in random_pins], f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
