from src.DB.CacheCollection import CacheCollection
from src.DB.PipelineGrade import PipelineGrade
from src.DB.Component import Component, Pin

from src.config import DB_URL, DB_COMPONENT_NAME

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

import asyncio
import nest_asyncio

_INIT_DB = False

async def init_db():
    print(f"Initializing database {DB_URL} for {DB_COMPONENT_NAME}")
    client = AsyncIOMotorClient(DB_URL)
    database = client[DB_COMPONENT_NAME]
    await init_beanie(database, document_models=[Component, CacheCollection, PipelineGrade])


loop = asyncio.get_event_loop()
if type(loop).__name__ != "Loop":  # Skip nest_asyncio if event loop is uvloop.Loop
    nest_asyncio.apply()

if loop.is_running():
    # If the event loop is already running, schedule init_db as a task
    asyncio.create_task(init_db())
else:
    loop.run_until_complete(init_db())
