import warnings
warnings.filterwarnings("ignore")

import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import nest_asyncio
nest_asyncio.apply()

from src.DB.Component import Component
from src.Pipeline import Pipeline
from src.PipelineSteps import FullPageExtractor, TextRag, LLMPinExtractor, LLMGrader
from src.LLM import Qwen25_VL_7B_Instruct, Qwen25_VL_32B_Instruct, GPT4oMini, Gemma3_VL_4B_Instruct, Gemma3_VL_27B_Instruct
from src.llm_inputs import RAG_QUERY_V1, LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, GRADING_INSTRUCTIONS_V1
from src.Pipeline.Grader import Grader
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.config import EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P, GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P
import asyncio


async def run_vision_pipeline():
    components = await Component.find().to_list()

    pipeline = Pipeline(pipeline_type="vision", grader=Grader())
    pipeline.add_step(FullPageExtractor(), exception_policy=ExceptionPolicy.TRY)
    pipeline.add_step(TextRag(RAG_QUERY_V1, num_results=4))
    pipeline.add_step([
        LLMPinExtractor(Qwen25_VL_7B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, llmOrVLM="vlm"),
        LLMPinExtractor(Qwen25_VL_32B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, llmOrVLM="vlm"),
        LLMPinExtractor(Gemma3_VL_4B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, llmOrVLM="vlm"),
        LLMPinExtractor(Gemma3_VL_27B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, llmOrVLM="vlm"),
    ], exception_policy=ExceptionPolicy.TRY, execution_policy=ExecutionPolicy.CACHE_ONLY)
    pipeline.add_step(LLMGrader(GPT4oMini(GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P), GRADING_INSTRUCTIONS_V1))

    grade, output = await pipeline(components, execution_policy=ExecutionPolicy.CACHE_ONLY)
    print("Grade: ", grade)

if __name__ == "__main__":
    asyncio.run(run_vision_pipeline())
