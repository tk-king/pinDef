import json
import os
from typing import Any
from pydantic import BaseModel

class VersionComponent(BaseModel):
    version: str
    content: Any

    def __add__(self, other: "VersionComponent") -> "VersionComponent":
        return VersionComponent(version=self.version + "_" + other.version, content=self.content + "\n" + other.content)

RAG_QUERY_V1 = VersionComponent(
    version="query_v1",
    content="pin-definitions pin-description pin-name pin-number pin-function 1, VDD, Supply voltage"
)

RAG_QUERY_V2 = VersionComponent(
    version="query_v2",
    content="""
        Pin definitions including pin number, pin name, and pin function or description from the datasheet. 
        Focus on extracting structured information about each pin.
        Example: 1, VDD, Supply voltage.
    """
)

LLM_QUESTION_V1 = VersionComponent(
    version="question_v1",
    content="""
            Which pins does the component have? List the name of the pin and also the function of the pin.
            Print a new line for each pin.
            Answer in valid json only.
            Answer with an array which contains objects.
            Each object contains a name attribute which indicates the name of the pin as specified in the datasheet.
            The second attribute is a description, which indicates the function of the pin as specified in the datasheet.
            The json-objects in the array shoud contain only the attribures "number", "name" and "description".
        """)


LLM_INSTRUCTIONS_V1 = VersionComponent(
    version="instructions_v1",
    content="""
            The output should be formatted as a JSON instance that conforms to the JSON schema below.
            The output contains of a list of objects.
            Each object in this list represents a pin of the component and follows this schema:
            {"number": "string", "name": "string", "description": "string"}.
            Therefore, a valid schema would be [{"number": "1", "name": "VCC", "description": "Power supply pin"}].
            Respond only with a valid JSON-List. Do not write an introduction or summary.
        """)


LLM_QUESTION_V2 = VersionComponent(
    version="question_v2",
    content="""
            What are the pins of the component listed in the datasheet? For each pin, provide:
            - The pin number.
            - The pin name.
            - The pin's function.
        """)

LLM_INSTRUCTIONS_V2 = VersionComponent(
    version="instructions_v2",
    content="""
            Format the output as a JSON array of objects, where each object represents a pin. Each object must contain:
            - "number" (string): The pin number from the datasheet.
            - "name" (string): The pin name from the datasheet.
            - "description" (string): The function of the pin, as described in the datasheet.

            Example of valid output:
            [{"number": "1", "name": "VCC", "description": "Power supply pin"}].

            Ensure the output is a valid JSON array and contains no extra text or explanations.
        """)

EXTRACTION_PROMPTS = {
    "v1": {"question": LLM_QUESTION_V1, "instructions": LLM_INSTRUCTIONS_V1},
    "v2": {"question": LLM_QUESTION_V2, "instrucitons": LLM_INSTRUCTIONS_V2}
}




GRADING_INSTRUCTIONS_V1 = VersionComponent(
    version="grading_instructions_v1",
    content="""
            You are given two json objects, one is the ground truth and the other one is generated data.
            Each json-object contains a "name" and a "description" field.
            When comparing the descriptions, ignore differences in punctuation, capitalization, extra spaces, and allow for significant variations in wording, phrasing, or synonyms, as long as the overall meaning is the same.
            Additionally, ignore common insignificant or filler words in the descriptions.
            Descriptions are considered semantically equal if they convey the same idea, even if expressed in different ways or with different vocabulary.
            When grading, be relaxed and forgiving about line breaks and formatting differences.
            Ignore whitespaces or separation characters such as "/", ";" or linebreaks in both the name and description fields.
            If the descriptions convey the same meaning, consider them equal.
            Output a json object with the following fields:
            - "name": boolean, whether the names are semantically equal
            - "description": boolean, whether the descriptions are semantically equal, ignoring differences in punctuation, capitalization, extra spaces, and allowing for significant variations in wording or phrasing
            Therefore, a valid example would be: {"name": true, "description": false}.
            Output only a valid JSON object. Do not write an introduction or summary.
            """
)

GRADING_INSTRUCTIONS_V2 = VersionComponent(
    version="grading_instructions_v2",
    content="""
            Compare the names of the two json objets. Are they the same, when ignoring differences in punctuation, capitalization, extra spaces?
            Also compare the descriptions of the two json objects. Do they mean the same thing even with different wording?
            Output a json object with the following fields:
            - "name": boolean, whether the names are semantically equal
            - "description": boolean, whether the descriptions are semantically equal, ignoring differences in punctuation, capitalization, extra spaces, and allowing for significant variations in wording or phrasing
            """
)


GRADING_PROMPTS = {
    "v1": {"instructions": GRADING_INSTRUCTIONS_V1}
}


# with open("pcbGPT/shot_examples.json") as f:
#     shot_examples = json.load(f)


# one_shot_text = shot_examples["one_shot"]["texts"]
# one_shot_pins = shot_examples["one_shot"]["pins"]

# LLM_ONE_SHOT_INSTRUCTIONS = VersionComponent(
#     version="one_shot_instructions_v1",
#     content = f"As an example, here is such a datasheet and the extracted pins: The datasheets: {one_shot_text} and the list of pins : {one_shot_pins}"
#     )


# few_shot_text = shot_examples["few_shot"]["texts"]
# few_shot_pins = shot_examples["few_shot"]["pins"]

# LLM_FEW_SHOT_INSTRUCTIONS = VersionComponent(
#     version="few_shot_instructions_v1",
#     content = """
#         Here are a few examples for your reference:
#         1. The datasheets: {few_shot_text[0]} and the list of pins : {few_shot_pins[0]} 
#         2. The datasheets: {few_shot_text[1]} and the list of pins : {few_shot_pins[1]}
#         3. The datasheets: {few_shot_text[2]} and the list of pins : {few_shot_pins[2]}
#         """
#     )


# LLM_COT_INSTRUCTIONS = VersionComponent(
#     version="cot_instructions_v1",
#     content = """Think deeply about this.

#         ### Step 1: Identify the Table
#         Look for a table in the datasheet that contains pin definitions. Tables usually contain columns such as:
#         - "Pin Name" / "Symbol"
#         - "Type" (Power, Input, Output, I/O, Ground, etc.)
#         - "Description" (Function of the pin)
        
#         ### Step 2: Extract the Pin Data
#         - Once the correct table is found, extract each row and organize it into a structured format.
#         - Check, that you have extracted each pins name, number, and description correctly.
#         - Check that there are no extra pins in your generated data.
#         - Check that no pin is missing from your generated data.

#         ### Step 3: Output the Results
#         Provide structured JSON output with flagged issues.

#     """
# )

# LLM_PERSONA_INSTRUCTIONS = VersionComponent(
#     version="persona_instructions_v1",
#     content = """
#         You are an expert semiconductor engineer with extensive experience in analyzing electronic component datasheets.
#         Your deep understanding of integrated circuits, microcontrollers, and other semiconductor devices allows you to accurately interpret and extract critical technical information. 
#         Additionally, you have a strong background in technical documentation, ensuring that extracted data is precise, well-structured, and faithful to the original datasheet content. 
#         Your expertise in semiconductor engineering and technical documentation enables you to provide high-quality pin extraction services that meet industry standards and client expectations.    
#         """
# )

INSTRUCTION_CONTEXT_TEMPLATE = """
            Use the following context to answer the question:
            {{context}}
        """
