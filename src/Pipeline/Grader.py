from pydantic import BaseModel, validate_call
from src.DB.Component import Component, Pin
from src.DB.CacheCollection import CacheCollection
from typing import List, Tuple, Union, Dict
from src.Utils.MergePins import merge_pins, MergedPin

import logging

logger = logging.getLogger(__name__)

class Grade(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    num_llm_pins: int


@validate_call
def calculate_metrics(pipeline_output: List[Tuple[Union[CacheCollection, None], Component]]) -> Grade:

    true_positives = 0 # Number of correctly identified pins
    true_negatives = 0 # Zero 
    false_positives = 0 # Number of incorrectly identified pins
    false_negatives = 0 # Number of pins that were not identified but should have been

    merged_pins = []
    for cache_collection, component in pipeline_output:
        if cache_collection is not None:
            merged_pins.extend(cache_collection.value)
        else:
            false_negatives += len(component.pins)

    new_merged_pins = []
    for pin in merged_pins:
        if type(pin) == dict:
            new_merged_pins.append(MergedPin(**pin))
        elif type(pin) == MergedPin:
            new_merged_pins.append(pin)
    merged_pins = new_merged_pins


    for pin in merged_pins:
        value = pin.name_correct is True and pin.description_correct is True
        if value:
            true_positives += 1
        else:
            false_positives += 1
    len_llm_extractions = sum(1 for x in merged_pins if x.llm_pins is not None)
    len_human_extractions = sum(1 for x in merged_pins if x.human_pin is not None)

    false_positives = max(0, len_llm_extractions - len_human_extractions) + false_positives
    false_negatives = max(0, len_human_extractions - len_llm_extractions) + false_negatives

    accuracy = (true_positives + true_negatives) / (true_positives + true_negatives + false_positives + false_negatives)
    precision = true_positives / (true_positives + false_positives)


    logger.info("True Positives: %d", true_positives)
    logger.info("True Negatives: %d", true_negatives)
    logger.info("False Positives: %d", false_positives)
    logger.info("False Negatives: %d", false_negatives)



    if (true_positives + false_negatives) == 0:
        raise Exception("No true positives or false negatives")
    else:
        recall = true_positives / (true_positives + false_negatives)

    logger.debug(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}")

    # Calculate F1 score
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    grade = Grade(
        accuracy = accuracy * 100,
        precision = precision * 100,
        recall = recall * 100,
        f1_score = f1_score * 100,
        num_llm_pins = sum(1 for x in merged_pins if x.llm_pins)
    )

    return grade


class Grader():

    @validate_call
    def __call__(self, inputs : List[Tuple[Union[CacheCollection, None], Component]]) -> Grade:
        return calculate_metrics(inputs)
