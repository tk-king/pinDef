from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

append_path_up = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, append_path_up)


from src.DB import init_db
from src.server.router.components import router as components_router
from src.server.router.random_grading import router as random_grading_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(components_router, prefix="/components", tags=["components"])
app.include_router(random_grading_router, prefix="/random_grading", tags=["random_grading"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
