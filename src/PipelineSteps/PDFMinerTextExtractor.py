from src.Pipeline import PipelineStep
from src.DB import CacheCollection, Component
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pdfminer.high_level import extract_text


class PDFMinerTextExtractor(PipelineStep):

    def __init__(self, chunk_size: int = 1024, overlap: int = 128):
        super().__init__()
        self.chunk_size = chunk_size
        self.overlap = overlap

    def step_key(self):
        return f"{self.chunk_size}_{self.overlap}"

    def get_display_name(self):
        return "PDFMiner"

    def invoke(self, input : Component, _: Component):
        text = extract_text(input.pdf_path)
        text = text.encode('utf-8').decode('utf-8')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.overlap)
        texts = text_splitter.split_text(text)
        texts = [{"text": text, "page": -1} for text in texts]
        return texts

