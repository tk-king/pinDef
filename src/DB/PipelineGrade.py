from beanie import Document
from typing import List, Optional

class PipelineGrade(Document):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    num_llm_pins: Optional[int] = None

    steps: List[str]
    key: str

    pipeline_type: str
    display_steps: List[str]