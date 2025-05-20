from fastapi import APIRouter, HTTPException
from glob import glob
from pydantic import BaseModel, Field
from typing import Union

import json

class Pin(BaseModel):
    number: str
    name : str
    description : str

class RandomGradingInput(BaseModel):
    expert_name_correct: Union[bool, None] = None
    expert_description_correct: Union[bool, None] = None

class MergedPin(BaseModel):
    llm_pins: Union[Pin, None] = None
    human_pin: Union[Pin, None] = None
    name_correct: Union[bool, None] = None
    description_correct: Union[bool, None] = None
    expert_grading: RandomGradingInput = Field(default_factory=RandomGradingInput)
    index : int

router = APIRouter()

import os

def load_json_files():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    file_path = os.path.join(base_path, "random_pins.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    data = [MergedPin(**{**item, "index":i}) for i, item in enumerate(data)]
    print("Num correct pins: ", len([item for item in data if item.llm_pins.name == item.human_pin.name]))
    print("Num all pins: ", len(data))
    return data

def save_json_files(data):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    file_path = os.path.join(base_path, "random_pins.json")
    with open(file_path, "w") as f:
        json.dump([item.dict() for item in data], f, indent=4)


@router.get("/")
async def get_components():
    return load_json_files()

@router.post("/")
async def update_component(component: MergedPin):
    data = load_json_files()
    if component.index >= len(data):
        raise HTTPException(status_code=404, detail="Component not found")
    data[component.index] = component
    save_json_files(data)
