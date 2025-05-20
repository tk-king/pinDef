import warnings
warnings.filterwarnings("ignore")

import sys

import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import nest_asyncio
nest_asyncio.apply()

from src.DB.Component import Component
from src.Pipeline import Pipeline
from src.PipelineSteps import OpenAIE2E, LLMGrader, GoogleGeminiE2E
from src.LLM import GPT4oMini
from src.llm_inputs import LLM_QUESTION_V2, LLM_INSTRUCTIONS_V2, GRADING_INSTRUCTIONS_V1
from src.Pipeline.Grader import Grader
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.config import GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P
import asyncio


async def run_proprietary_pipeline():
    components = await Component.find().to_list()

    openaiE2E_pipeline = Pipeline(grader=Grader(), pipeline_type="proprietary")
    openaiE2E_pipeline.add_step([
        OpenAIE2E(model="gpt-4o-mini", instructions=LLM_INSTRUCTIONS_V2, question=LLM_QUESTION_V2),
        GoogleGeminiE2E(model="gemini-2.0-flash", instructions=LLM_INSTRUCTIONS_V2, question=LLM_QUESTION_V2),
        OpenAIE2E(model="gpt-4o", instructions=LLM_INSTRUCTIONS_V2, question=LLM_QUESTION_V2),
    ], exception_policy=ExceptionPolicy.TRY, execution_policy=ExecutionPolicy.CACHE_ONLY)

    openaiE2E_pipeline.add_step(LLMGrader(llm=GPT4oMini(GRADING_LLM_TEMPERATURE, GRADING_LLM_TOP_P), grading_instructions=GRADING_INSTRUCTIONS_V1), exception_policy=ExceptionPolicy.THROW)

    print(openaiE2E_pipeline)
    grade, _ = await openaiE2E_pipeline(components, execution_policy=ExecutionPolicy.CACHE_ONLY)
    print(grade)

if __name__ == "__main__":
    asyncio.run(run_proprietary_pipeline())
