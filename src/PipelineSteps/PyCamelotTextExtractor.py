from src.Pipeline import PipelineStep
from src.DB import Component

from typing import List
import camelot

class PyCamelotTextExtractor(PipelineStep):
    def __init__(self):
        super().__init__()

    def step_key(self):
        return ""
    
    def get_display_name(self):
        return "PyCamelot"

    def _process_table(self, df):
        head = df.to_numpy()[0]
        body = df.to_numpy()[1:]
        table_str = "<TABLE>\n"
        join_head = ",".join(head).replace("\n", "")
        table_str += f"<HEAD>{join_head}</HEAD>"
        for row in body:
            row = [cell.replace("\n", "") if cell is not None else "" for cell in row]
            table_str += f"<ROW>{','.join(row)}</ROW>\n"
        table_str += "</TABLE>"
        return table_str
    
    def invoke(self, component: Component, _: Component) -> List[str]:
        page_text = ""

        texts = []
        # page_texts = []
        # with pdfplumber.open(component.pdf_path) as pdf:
        #     for page in pdf.pages:
        #         page_texts.append(page.extract_text())

        pin_tables = camelot.read_pdf(component.pdf_path, pages="all")
        for table in pin_tables:
            extracted_table = self._process_table(table.df)
            texts.append({"text": extracted_table, "page": table.page -1})
        # for i, page_text in enumerate(page_texts):
        #     texts.append({"text": page_text, "page": i})
        return texts