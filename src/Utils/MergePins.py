from typing import Union, List
from pydantic import BaseModel
from src.DB.Component import Pin, Component
from pydantic import validate_call

class MergedPin(BaseModel):
    llm_pins: Union[Pin, None] = None
    human_pin: Union[Pin, None] = None
    name_correct: Union[bool, None] = None
    description_correct: Union[bool, None] = None


@validate_call
def merge_pins(component: Component, pin_list: List[Pin]) -> List[MergedPin]:
    merged_pins = []
    for pin in component.pins:
        pin_number = pin.number
        llm_pin = None
        for l_pin in pin_list:
            if l_pin.number == pin_number:
                llm_pin = l_pin
                break
        if llm_pin is not None:
            llm_pin = Pin(**llm_pin.dict())
        merged_pin = MergedPin(llm_pins=llm_pin, human_pin=pin)
        merged_pins.append(merged_pin)
    
    for llm_pin in pin_list:
        if llm_pin.number not in [pin.number for pin in component.pins]:
            merged_pin = MergedPin(llm_pins=llm_pin, human_pin=None)
            merged_pins.append(merged_pin)
    return merged_pins