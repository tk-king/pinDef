import warnings
warnings.filterwarnings("ignore")

import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import nest_asyncio
nest_asyncio.apply()

from src.DB.Component import Component
from src.Pipeline import Pipeline
from src.PipelineSteps import PyCamelotTextExtractor, PDFMinerTextExtractor, TextRag, LLMPinExtractor, LLMGrader
from src.LLM import GPT4oMini, Llama31_8B, Qwen25_7B_Instruct, Qwen25_72B_Instruct_AWQ
        
from src.llm_inputs import RAG_QUERY_V1, LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, GRADING_INSTRUCTIONS_V1
from src.Pipeline.Grader import Grader
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.config import EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P, GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P
import asyncio


async def run_text_pipeline():
    components = await Component.find().to_list()
    
    text_pipeline = Pipeline(grader=Grader(), pipeline_type="text")
    text_pipeline.add_step([
        PyCamelotTextExtractor(),
        PDFMinerTextExtractor(chunk_size=1024, overlap=128),
    ], exception_policy=ExceptionPolicy.TRY)
    text_pipeline.add_step(TextRag(RAG_QUERY_V1))
    text_pipeline.add_step([
        LLMPinExtractor(Qwen25_7B_Instruct(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2),
        LLMPinExtractor(Qwen25_72B_Instruct_AWQ(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2),
        LLMPinExtractor(Llama31_8B(EXTRACTION_LLM_TEMPERATURE, EXTRACTION_LLM_TOP_P), LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2),
        ], execution_policy=ExecutionPolicy.CACHE_ONLY)
    text_pipeline.add_step(LLMGrader(llm=GPT4oMini(GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P), grading_instructions=GRADING_INSTRUCTIONS_V1), exception_policy=ExceptionPolicy.THROW)

    grade, output = await text_pipeline(components, execution_policy=ExecutionPolicy.CACHE_ONLY)
    print("Grade: ", grade)

if __name__ == "__main__":
    asyncio.run(run_text_pipeline())
