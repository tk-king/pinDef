from beanie import Document
from typing import List
from pydantic import BaseModel, Field
from src.Utils.PDFDownloader import download_pdf
from typing import Optional
import re

import os


class Pin(BaseModel):
    number: str
    name : str
    description : str

class Component(Document):
    name: str = Field(..., min_length=1)
    manufacturer: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    pins: List[Pin] = Field(..., min_length=1)
    version: str
    url: str = Field(..., min_length=1)
    pages: str
    flag: Optional[str] = None

    @property
    def pdf_path(self):

        def sanitize_path(filename):
            filename = re.sub(r'[()/]', '', filename)   # remove parentheses
            filename = filename.replace('/', '_')       # replace slash with underscore
            filename = filename.replace(' ', '_')       # replace spaces with underscores
            return filename        # Ensure the PDF path is sanitized

        file_name = sanitize_path(self.name)
        pdf_path = os.path.join("pdf_folder", f"{file_name}.pdf")
        return pdf_path
    
    def download_pdf(self):
        return download_pdf(self, self.pdf_path)
    
    def __hash__(self):
        return hash(self.id)
    
    @classmethod
    async def get_all_grouped(cls, group_by: str = "manufacturer", custom_reduce_fn=None, only_pdf=False, min_group_size=1):
        all_components = await cls.find_all().to_list()
        all_components = [c for c in all_components if "sensor" in c.type.lower()]
        
        if only_pdf:
            all_components = [comp for comp in all_components if comp.pdf_path]

        grouped_components = {}

        for component in all_components:
            attr = getattr(component, group_by)
            if custom_reduce_fn:
                attr = custom_reduce_fn(attr)
            if attr not in grouped_components:
                grouped_components[attr] = []
            grouped_components[attr].append(component)

        # Move groups smaller than `min_group_size` to "other"
        grouped_filtered = {}
        grouped_filtered["Other"] = []

        for key, group in grouped_components.items():
            if len(group) >= min_group_size:
                grouped_filtered[key] = group
            else:
                grouped_filtered["Other"].extend(group)

        # Remove "other" if empty and not needed
        if not grouped_filtered["Other"]:
            del grouped_filtered["Other"]

        return grouped_filtered
