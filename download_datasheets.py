from src.DB.Component import Component
import asyncio
from tqdm import tqdm

async def download_datasheets():
    components = await Component.find().to_list()
    for component in tqdm(components):
        await component.download_pdf()

if __name__ == "__main__":
    asyncio.run(download_datasheets())