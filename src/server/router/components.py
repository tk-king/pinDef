from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from beanie import PydanticObjectId
import os

from src.DB.Component import Component

import json

router = APIRouter()


@router.get("/")
async def get_components():
    return await Component.find({}).to_list()

@router.get("/download")
async def download_components():
    components = await Component.find({}).to_list()
    return components


@router.post("/")
async def create_component(component: Component):
    await component.insert()
    return component

@router.put("/{component_id}")
async def update_component(component_id: str, component: Component):
    existing_component = await Component.get(component_id)
    if not existing_component:
        return {"error": "Component not found"}
    await existing_component.update({"$set": component.model_dump()})
    return existing_component

import httpx
from fastapi.responses import StreamingResponse
from urllib.parse import unquote

@router.get("/pdf")
async def get_pdf(url: str, name: str = None):
    print("URL:", url)
    print("Name:", name)

    print(url)
    decoded_url = unquote(url)

    try:
        if name is not None:
            file_path = os.path.join("..", "pdf_folder", name + ".pdf")
            print("Reading from file:", file_path)
            with open(file_path, "rb") as f:
                pdf_data = f.read()
            if pdf_data:
                return FileResponse(
                    file_path,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "inline; filename=document.pdf"}
                )
    except FileNotFoundError:
        pass


    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            print("Fetching from URL:", decoded_url)
            response = await client.get(
                decoded_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:117.0) Gecko/20100101 Firefox/117.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.mouser.com/"
                }
            )
            response.raise_for_status()
            return StreamingResponse(
                response.aiter_bytes(),
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=document.pdf"}
            )
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise e
        return JSONResponse(content={"error": "Failed to download file"}, status_code=400)
