import time
import json
import logging
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
from typing import List, Dict


import base64

def encode_image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

max_retries = 3
model = 'llama3.2-vision'

def query_llm(prompt: str, instruction_set: str, llm_role:str, response_key: str, img_path : str) -> Dict:
    """
    Queries the LLM with retries.

    Args:
        prompt (str): The input prompt for the LLM.
        instruction_set (str): Instruction set for the LLM.

    Returns:
        Dict: Parsed response from the LLM.
    """
    for attempt in range(max_retries):
        try:
            llm = ChatOllama(model=model, temperature=0.1, format="json")
            image_b64 = encode_image_to_base64(img_path)
            response = llm.invoke(
                [SystemMessage(content=instruction_set)] +
                [HumanMessage(content=(
            f"{prompt}\n\n"
            f"Here is the image in Base64:\n\n"
            f"{image_b64}"
        ))]
            )
            print(response)
            response_content = response.content.strip()
            return parse_llm_response(response_content, response_key, llm_role)
        except Exception as e:
            logger.error(f"Error querying LLM {llm_role} (Attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

def parse_llm_response(response: str, response_key: str, llm_role:str ) -> Dict:
    """
    Parses the LLM response.

    Args:
        response (str): The response content from the LLM.

    Returns:
        Dict: Parsed response if valid.
    """
    try:
        parsed_response = json.loads(response)
        if isinstance(parsed_response, dict) and response_key in parsed_response:
            return parsed_response
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed for llm {llm_role}: {e}")
    return {}

# Logo Classifier Agent
def is_logo_image(img_path: str) -> bool:

    instruction_set = (
        "You are an expert visual analyzer for determining the content of images. You can parse the contents in the image"
    )

    prompt = f"Please parse the image"
    prompt += "\nRespond in JSON format as follows:\n"
    prompt += "{ 'description': 'Any additional information' }"

    llm_role = "Logo Classifier"
    response_key = "description"

    parsed_response = query_llm(prompt, instruction_set, llm_role, response_key, img_path)

    logger.info(f"Agent {llm_role} : Parsed Response: {parsed_response}")

    if parsed_response:
        if "description" in parsed_response and parsed_response["description"] in ["Yes", "No"]:
            return parsed_response["description"]
        else:
            logger.error(f"Agent {llm_role} : Invalid JSON structure or missing 'is_logo' key. Hence classifying it as logo.")
    else:
        logger.error(f"Agent {llm_role} : Image classification failed after multiple attempts. Hence classifying it as logo.")
    
    return True


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger("RevParser")

    img_path = r"/home/revdha/PycharmProjects/RAG Projects/datastore/ParsedFiles/PB-10.3-1_Fortlaufende_Verbesserung/_page_2_Figure_8.jpeg"

    is_logo_image(img_path)
