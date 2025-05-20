from dotenv import load_dotenv
import os
from src.Utils.latex_vars import LatexVars

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

DB_COMPONENT_NAME = os.getenv("DB_COMPONENT_NAME", "components")
DB_URL = os.getenv("DB_URL")
LATEX_DIR = os.getenv("LATEX_DIR", "./LATEX_DIR")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


# LLM Settings
EXTRACTION_LLM_TOP_P = 0.2
EXTRACTION_LLM_TEMPERATURE = 0.1

GRADING_LLM_TOP_P = 0.2
GRADING_LLM_TEMPERATURE = 0.1

MAX_GENERATION_TOKEN = 1024*4


OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"


latexVars = LatexVars(LATEX_DIR)
latexVars["EXTRACTIONLLMTOPP"] = EXTRACTION_LLM_TOP_P
latexVars["EXTRACTIONLLMTEMPERATURE"] = EXTRACTION_LLM_TEMPERATURE
latexVars["GRADINGLLMTOPP"] = GRADING_LLM_TOP_P
latexVars["GRADINGLLMTEMPERATURE"] = GRADING_LLM_TEMPERATURE
latexVars["MAXGENERATIONTOKEN"] = MAX_GENERATION_TOKEN

latexVars["OPENAIEMBEDDINGSMODEL"] = OPENAI_EMBEDDINGS_MODEL
