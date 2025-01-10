from pathlib import Path
from typing import List, Dict
from shutil import rmtree, move
from datetime import datetime
from pydantic import BaseModel
from ollama import Options, chat
import uuid
import json
import logging
import time
import os


class ImageProcessor:
    """
    Processes images to determine if they are logos or contain information,
    and extracts relevant details into a Markdown file.
    """

    def __init__(self, folder_path: str, model: str = 'llama3.2-vision', logger: logging.Logger = None, translator: bool = False, qa_evaluator:bool = True):
        """
        Initializes the ImageProcessor.

        Args:
            folder_path (str): Path to the folder containing images and a Markdown file.
            model (str): Name of the Ollama model to use.
            logger (logging.Logger, optional): Logger instance to use for logging. Defaults to None.
            translator (bool, optional): Whether to enable translation of extracted content. Defaults to False.
            qa_evaluator (bool, optional): Whether to enable QA evaluation for selecting the best response during image processing. Defaults to True.
        """

        self.folder_path = Path(folder_path)
        self.model = model
        self.results: List[Dict[str, str]] = []
        self.max_retries = 3
        self.img_language = "English"
        self.translator = translator
        self.qa_evaluator = qa_evaluator

        # Use provided logger or set up a default logger
        self.logger = logger or logging.getLogger(__name__)

        # Automatically locate the markdown file
        markdown_files = list(self.folder_path.glob("*.md"))
        if not markdown_files:
            raise FileNotFoundError(f"No Markdown (.md) file found in {self.folder_path}.")
        elif len(markdown_files) > 1:
            raise ValueError(f"Multiple Markdown (.md) files found in {self.folder_path}: {markdown_files}. Please ensure only one is present.")
        
        # Assign the detected markdown file
        self.markdown_file = markdown_files[0]
        self.markdown_file_name = self.markdown_file.stem
        self.logger.info(f"Using Markdown file: {self.markdown_file}")

    def process_images(self) -> None:
        """
        Processes all PNG images in the folder by querying the Ollama model.
        """
        image_files = list(self.folder_path.glob("*.png")) + \
                      list(self.folder_path.glob("*.jpg")) + \
                      list(self.folder_path.glob("*.jpeg"))

        for image_file in image_files:
            self.logger.info(f"Processing image: {image_file.name}")
            result = self.process_image(image_file)
            self.results.append(result)

    def process_image(self, image_path: Path) -> Dict[str, str]:
        """
        Processes a single image by classifying if it's a logo and extracting information.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            Dict[str, str]: Processed results.
        """
        if not self.is_logo_image(image_path):
            new_image_path = self.move_image_to_pics_folder(image_path)
            self.logger.info(f"Operating in QA {self.qa_evaluator} mode")
            if self.qa_evaluator:
                responses = self.extract_information_multiple_times(new_image_path, max_responses=3)
                best_response_index = self.determine_best_response(responses, new_image_path)
                best_response = responses[best_response_index - 1]
            else:
                responses = self.extract_information_multiple_times(new_image_path, max_responses=1)
                best_response = responses[0]
            if self.translator:
                translated_response = self.translate_response_to_original_language(best_response, new_image_path)
            else:
                translated_response = best_response
        else:
            self.logger.info(f"The image {image_path.name} is classified as a company logo. No further processing required.")
            return self.create_result(old_image_path=image_path, new_image_path=image_path, is_logo=True, contains_info=False, extracted_info="N/A")

        return self.create_result(old_image_path=image_path, new_image_path=new_image_path, is_logo=False, contains_info=True, extracted_info=translated_response)

    # Logo Classifier Agent
    def is_logo_image(self, img_path: str) -> bool:

        instruction_set = """
        You are an image classifier specialized in determining whether an image is a logo or not.

        1. Classify the image as a logo only if it primarily contains:
        - Symbols, icons, or graphical elements with minimal or no text.
        - Simple text combined with symbols or icons, where the focus remains on the graphical element.
        - Simple text regarding the page number or just few words
        - Simple text such as company name or footer notes
        
        2. Do NOT classify the image as a logo if it contains:
        - Detailed information like paragraphs, long text, or multiple lines of text.
        - Complex visual elements such as tables, flowcharts, infographics, or diagrams.
        - Multiple distinct components indicating it is a document or a visual representation of data.

        3. If unsure, classify the image as not a logo to minimize false positives.
        """

        prompt = "Please classify the image as a logo or not."
        prompt += "\nEnsure the following criteria are met for classification:"
        prompt += "\n- Classify as a logo only if the image primarily contains logos."
        prompt += "\n- If the image contains detailed content like paragraphs, tables, diagrams, or flowcharts, classify it as not a logo."
        prompt += "\n- If unsure, classify the image as not a logo."
        prompt += "\nRespond in JSON format as follows:\n"
        prompt += "{ 'is_logo': True or False }"

        # Define the schema for the response
        class logo_agent_schema(BaseModel):
            is_logo: bool

        llm_role = "Logo Classifier"
        response_key = "is_logo"
        llm_schema = logo_agent_schema.model_json_schema()

        return self.retry_ollama_vision_agent(instruction_set, prompt, llm_role, response_key, img_path, llm_schema)

    #  Information Extractor Agent
    def extract_information_multiple_times(self, img_path: str, max_responses: int = 3) -> List[str]:
        """
        Extracts information from an image multiple times to ensure accuracy.

        Args:
            img_path (str): Path to the image file.
            max_responses (int): Maximum number of responses to collect.

        Returns:
            List[str]: Extracted information from the image.
        """

        instruction_set = """
        
        You are a precise visual content analyzer specialized in extracting information from images. 
        Your task is to methodically identify, analyze, and structure information from images containing text, tables, graphs, and/or flowcharts.

        # Core Responsibilities
        1. Analyze the image thoroughly and identify all present elements
        2. Extract information with exact precision - no assumptions or fabrications
        3. Structure the output according to detected elements only
        4. Maintain consistent formatting for each element type

        # Processing Guidelines
        - Detect language and maintain extraction in original language
        - Preserve exact numerical values, labels, and text as shown
        - Report only what is visibly present in the image
        - Skip sections that don't apply to the current image
        - Maintain proper data relationships in tables and graphs
        - Preserve flow direction and connections in flowcharts

        # Required Output Format

        ```markdown
        # Image Analysis Results

        ### Detected Elements
        - Elements: [List only found elements: Text, Table, Graph, Flowchart]
        - Language: [Primary language detected]
        
        ### Overview
        [Brief summary of the image content]

        ### Text Content
        {Include only if text is present}
        [Direct transcription of visible text, preserving formatting]

        ### Table Content
        {Include only if table is present}
        ##### Table: [Title if present]
        | Header 1 | Header 2 | ... |
        |----------|----------|-----|
        | Value    | Value    | ... |

        ### Graph Analysis
        {Include only if graph is present}
        ##### Graph: [Title if present]
        - **Type**: [Line/Bar/Pie/Scatter/etc.]
        - **X-axis**: [Label] (units if shown)
        - **Y-axis**: [Label] (units if shown)
        - **Legend**: [Items if present]
        - **Data Points**:
        - [(x1, y1)]
        - [(x2, y2)]
        - [Additional significant points]

        ### Flowchart Structure
        {Include only if flowchart is present}
        ##### Flowchart: [Title if present]
        - **Components**:
        1. [Node 1]: [Exact text]
        2. [Node 2]: [Exact text]

        - **Connections**:
        - [Node 1] → [Node 2]: [Connection label if any]
        - [Node 2] → [Node 3]: [Connection label if any]
        ```

        # Quality Requirements
        1. Include ONLY sections for elements actually present in the image
        2. Extract content EXACTLY as shown - no interpretation or assumptions
        3. Mark unclear elements as [Partially Visible] or [Unclear]
        4. Maintain all numerical values exactly as displayed
        5. Preserve original language and formatting
        6. Report any extraction issues in the respective section

        # Common Errors to Avoid
        - Do not create or infer missing data
        - Do not include sections for elements not in the image
        - Do not modify or "improve" unclear text
        - Do not change numerical formats or units
        - Do not translate content unless specifically requested

        # Error Reporting Format
        If content is unclear or partially visible:
        - Mark with [Unclear] or [Partially Visible]
        - Note specific issue (e.g., "Bottom right corner obscured")
        - Do not attempt to reconstruct unclear elements

        Remember: Accuracy and precision are paramount. Output only what you can see with absolute certainty.

        """

        prompt = "Please extract information from the image."
        prompt += "\nRespond in JSON format as follows:\n"
        prompt += """{
            "Detected Elements": "[List only found elements: Text, Table, Graph, Flowchart]",
            "Language": "[Primary language detected]",
            "Text Content": "[Detailed overview of the image]",
        }"""

        # Define the schema for the response
        class information_extractor_schema(BaseModel):
            Detected_Elements: List[str]
            Language: str
            Text_Content: str

        llm_role = "Information Extractor"
        response_key = "Text Content"
        llm_schema = information_extractor_schema.model_json_schema()

        results = []
    
        for response_index in range(max_responses):  # Collect 3 responses
            self.logger.info(f"Extracting information from image: {img_path} (Collection {response_index + 1})")
            result = self.retry_ollama_vision_agent(instruction_set, prompt, llm_role, response_key, img_path, llm_schema)
            results.append(result)
        
        return results

    # QA Evaluator Agent
    def determine_best_response(self, responses: List[str], img_path: str) -> int:
        """
        Determines the best response among multiple extracted information responses.
        
        Args:
            responses (List[str]): List of extracted information responses.
            img_path (str): Path to the image file.
        
        Returns:
            int: Index of the best response in the list.
        """

        concatenated_responses = "\n\n".join([f"Response {i+1}:\n{resp}" for i, resp in enumerate(responses)])

        instruction_set = """
        You are a QA evaluator specializing in selecting the best response that accurately and comprehensively explains the content of an image.

        You will be provided with three responses for the same task. Your job is to select the response that provides:
        1. The most detailed and accurate explanation of the information for the content type present in the image.
        2. A complete description of the key elements, structure, and relationships in the image, especially for content types such as flowcharts, diagrams, or complex visuals.

        Evaluation Criteria:
        - Prioritize responses that thoroughly explain the content, covering all key elements, even if they are longer.
        - Ensure the selected response provides clear and structured information, including details about the relationships or flow if applicable (e.g., in flowcharts, tables, or graphs).
        - Avoid selecting responses that are too brief or omit key parts of the content.

        Tie-Breaker Rule:
        - If two or more responses seem equally good, choose the one that offers slightly more clarity, organization, or critical detail.

        """

        prompt = "Please select the best response from the three responses provided. Each response is labeled with a response index (1, 2, or 3)."
        prompt += "\n\nHere are the responses:\n"

        # Example of how to concatenate responses with indices
        for idx, response in enumerate(responses, 1):
            prompt += f"Response Index {idx} : \n {response}\n\n"

        prompt += "\nRespond in JSON format as follows:\n"
        prompt += "{ 'best_response': 1 or 2 or 3 }"


        # Define the schema for the response
        class qa_evaluator_schema(BaseModel):
            best_response: int

        llm_role = "QA Evaluator"
        response_key = "best_response"
        llm_schema = qa_evaluator_schema.model_json_schema()

        return self.retry_ollama_vision_agent(instruction_set, prompt, llm_role, response_key, img_path, llm_schema, [1, 2, 3])
            
    # Translator Agent
    def translate_response_to_original_language(self, response: str, img_path: str) -> str:
        
        instruction_set = (
            f"You are a translator. Your job is to translate the text into {self.img_language}. "
            "Provide only the translated text with no additional comments, explanations, or formatting.\n\n"
        )

        prompt = f"Please translate the text into {self.img_language}."
        prompt += f"\n{response}\n\n"
        prompt += "\nRespond in JSON format as follows:\n"
        prompt += "{ 'translated_text': '[Translated text in the target language]' }"

        # Define the schema for the response
        class translator_schema(BaseModel):
            translated_text: str

        llm_role = "Translator"
        response_key = "translated_text"
        llm_schema = translator_schema.model_json_schema()

        return self.retry_ollama_vision_agent(instruction_set, prompt, llm_role, response_key, img_path, llm_schema)

    def update_markdown(self) -> None:
        """
        Updates the Markdown file with extracted information for images,
        moves the updated file to the parent directory, and deletes the old folder.
        """
        self.logger.info(f"Updating Markdown file: {self.markdown_file}")
        if not self.markdown_file.exists():
            self.logger.error(f"Markdown file {self.markdown_file} does not exist.")
            return

        with open(self.markdown_file, "r", encoding="utf-8") as md_file:
            content = md_file.read()

        self.logger.info(f"Read Markdown content")

        for result in self.results:
            if result["contains_info"]:
                # Add extracted info as a comment below the image reference in Markdown
                base_path = Path.cwd()
                relative_path = os.path.relpath(result['new_image_path'], start=base_path)
                image_ref = f"![]({result['image']})"
                extracted_info = result['extracted_info']
                updated_extracted_info = f"[![Extracted Image]({relative_path})]({relative_path}) \n {extracted_info}"
                content = content.replace(image_ref, updated_extracted_info)
            else:
                image_ref = f"![]({result['image']})"
                content = content.replace(image_ref, "")

        self.logger.info(f"Updated Markdown content")
        # Save the updated file in the parent folder
        updt_file_path = self.folder_path.parent / f"{self.markdown_file.name}"
        with open(updt_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(content)
        self.logger.info(f"Updated Markdown file saved at: {updt_file_path}")

        # Check and delete the folder containing the old markdown file
        markdown_folder = self.markdown_file.parent
        rmtree(markdown_folder)
        self.logger.info(f"Deleted folder containing old Markdown file: {markdown_folder}")

    def summarize_results(self) -> None:
        """
        Prints a summary of the processed results.
        """
        self.logger.info("Summary of Results:")
        for result in self.results:
            self.logger.info(f"Image: {result['image']}")
            self.logger.info(f"Old Image Path: {result['old_image_path']}")
            self.logger.info(f"New Image Path: {result['new_image_path']}")
            self.logger.info(f"  - Is Logo: {result['is_logo']}")
            self.logger.info(f"  - Contains Info: {result['contains_info']}")
            self.logger.info(f"  - Extracted Info: {result['extracted_info']}")

    def move_image_to_pics_folder(self, image_path: Path, with_timestamp: bool = False) -> Path:
        """
        Moves the image to the 'pics' folder and returns the new image path.

        Args:
            image_path (Path): Path to the image file.

        Returns:
            Path: New image path.
        """
        pics_folder = self.folder_path.parent / "pics"
        pics_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]

        if with_timestamp:
            new_image_path = pics_folder / f"{self.markdown_file_name}{image_path.stem}_{timestamp}_{unique_id}{image_path.suffix}"
        else:
            new_image_path = pics_folder / f"{self.markdown_file_name}{image_path.stem}{image_path.suffix}"

        move(str(image_path), str(new_image_path))

        return new_image_path

    def create_result(self, old_image_path: Path, new_image_path: Path, is_logo: bool, contains_info: bool, extracted_info: str) -> Dict[str, str]:
        """
        Creates a result dictionary for the processed image.

        Args:
            old_image_path (Path): Path to the old image file.
            new_image_path (Path): Path to the new image file.
            is_logo (bool): Whether the image is a logo.
            contains_info (bool): Whether the image contains information.
            extracted_info (str): Extracted information from the image.

        Returns:
            Dict[str, str]: Result dictionary.
        """
        return {
            "image": old_image_path.name,
            "old_image_path": str(old_image_path),
            "new_image_path": str(new_image_path),
            "is_logo": is_logo,
            "contains_info": contains_info,
            "extracted_info": extracted_info
        }
    
    def ollama_vision_agent(self, instruction_set: str, user_prompt: str, img_path: str, llm_schema: str) -> str:
        """
        Calls the Ollama vision agent to process an image.
        
        Args:
            instruction_set (str): Instructions for the agent.
            user_prompt (str): User prompt for the agent.
            img_path (str): Path to the image file.
            llm_schema (str): JSON schema for the response.
            
        Returns:
            str: Response from the agent.
        """
        response = chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': instruction_set,
                    'images': [img_path]
                },

                {
                    'role': 'user',
                    'content': user_prompt,
                    'images': [img_path]
                }
            ],
            format='json',
            options={'temperature': 0.7}
        )
        return response['message']['content']
    
    
    def retry_ollama_vision_agent(self, instruction_set: str, user_prompt: str, llm_role: str, response_key: str, img_path: str, llm_schema: str, valid_values: List = []) -> str:
        """
        Retries calling the Ollama vision agent until a valid response is received.

        Args:
            instruction_set (str): Instructions for the agent.
            user_prompt (str): User prompt for the agent.
            llm_role (str): Name of the agent.
            response_key (str): Key to extract from the response.
            img_path (str): Path to the image file.
            llm_schema (str): JSON schema for the response.

        Returns:
            str: Valid value for the key.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.ollama_vision_agent(instruction_set, user_prompt, img_path, llm_schema)
                response_json = json.loads(response)

                if response_key in response_json:
                    if valid_values:
                        if response_json[response_key] in valid_values:
                            self.logger.info(f"Agent {llm_role} : Response: {response_json[response_key]}")
                            return response_json[response_key]
                        else:
                            raise ValueError(f"Agent {llm_role} : Invalid response value: {response_json[response_key]}")
                    else:
                        if llm_role == "Information Extractor":
                            self.img_language = list(response_json['Language'])[0]
                        return response_json[response_key]
                else:
                    raise ValueError(f"Agent {llm_role} : Invalid JSON structure or missing '{response_key}' key.")
            except json.JSONDecodeError:
                self.logger.error(f"Agent {llm_role} : Attempt {attempt + 1}: Response is not valid JSON: {response}")
            except Exception as e:
                self.logger.error(f"Agent {llm_role} : Attempt {attempt + 1}: Error during classification: {e}")

            if attempt < self.max_retries - 1:
                time.sleep(1)
            else:
                self.logger.error(f"Operation failed after {self.max_retries} attempts.")
                raise RuntimeError(f"Operation failed after {self.max_retries} attempts.")

        return ""


if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process images and query the Ollama model.")
    parser.add_argument("folder", type=str, help="Path to the folder containing images.")
    parser.add_argument("--model", type=str, default='llama3.2-vision', help="Ollama model to query.")
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger("LlaMarker")

    # Create an instance of ImageProcessor
    processor = ImageProcessor(args.folder, args.model, logger)

    # Process images
    processor.process_images()

    # Update Markdown file with extracted info
    processor.update_markdown()

    # Print summary of results
    processor.summarize_results()
