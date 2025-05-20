from src.Pipeline import PipelineStep
from src.DB import CacheCollection, Component
import pdfplumber
from typing import List


class FullPageExtractor(PipelineStep):

    def __init__(self):
        super().__init__()

    def step_key(self):
        return "full_pages"

    def get_display_name(self):
        return "PDFPlumberPagewise"

    def invoke(self, input: Component, _: Component) -> List[dict]:
        all_page_texts = []

        with pdfplumber.open(input.pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                all_page_texts.append({
                    "text": page_text.strip(),
                    "page": page_number
                })

        return all_page_texts
