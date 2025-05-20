import pdfplumber
from src.Pipeline import PipelineStep
from src.DB import Component


class PDFPlumberTextExtractor(PipelineStep):
    def __init__(self):
        super().__init__()

    def step_key(self):
        return "tables_only"

    def get_display_name(self):
        return "PDFPlumber"

    def sanitize_cell(self, cell):
        """Ensure all cells are strings and not None."""
        return str(cell).strip() if cell is not None else ""

    def invoke(self, input: Component, _: Component):
        table_chunks = []

        with pdfplumber.open(input.pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue  # Skip empty or header-only tables

                    # Sanitize header and rows
                    header = [self.sanitize_cell(cell) for cell in table[0]]
                    rows = [
                        [self.sanitize_cell(cell) for cell in row]
                        for row in table[1:]
                    ]

                    # Convert to Markdown
                    markdown = f"### Table on Page {page_number}\n\n"
                    markdown += "| " + " | ".join(header) + " |\n"
                    markdown += "|" + " --- |" * len(header) + "\n"
                    for row in rows:
                        markdown += "| " + " | ".join(row) + " |\n"

                    table_chunks.append({
                        "text": markdown,
                        "page": page_number
                    })

        return table_chunks