from pathlib import Path
from typing import List, Dict
from shutil import rmtree, move
from datetime import datetime
import ollama
import uuid
import json
import logging
import time


class ImageProcessor:
    """
    Processes images to determine if they are logos or contain information,
    and extracts relevant details into a Markdown file.
    """

    def __init__(self, folder_path: str, model: str = 'llama3.2-vision', logger: logging.Logger = None):
        """
        Initializes the ImageProcessor.

        Args:
            folder_path (str): Path to the folder containing images and a Markdown file.
            model (str): Name of the Ollama model to use.
            logger (logging.Logger): Logger instance to use for logging.
        """
        self.folder_path = Path(folder_path)
        self.model = model
        self.results: List[Dict[str, str]] = []

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
            # Create 'pics' folder in the parent directory
            pics_folder = self.folder_path.parent / "pics"
            pics_folder.mkdir(parents=True, exist_ok=True)

            # Move the image to the 'pics' folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]

            new_image_path = pics_folder / f"{image_path.stem}_{timestamp}_{unique_id}{image_path.suffix}"
            move(str(image_path), str(new_image_path))

            # Update the image path
            image_path = new_image_path

            responses = self.extract_information_multiple_times(image_path)
            best_response_index = self.determine_best_response(responses, image_path)
            best_response = responses[best_response_index - 1]
            translated_response = self.translate_response_to_original_language(best_response, image_path)
        else:
            self.logger.info(f"The image {image_path.name} is classified as a company logo. No further processing required.")
            
            return {
                "image": image_path.name,
                "image_path": str(image_path),
                "is_logo": True,
                "contains_info": False,
                "extracted_info": "N/A"
            }

        return {
            "image": image_path.name,
            "image_path": str(image_path),
            "is_logo": False,
            "contains_info": True,
            "extracted_info": translated_response
        }

    def is_logo_image(self, img_path: str) -> bool:
        role_1 = (
            "You are an image classifier specialized in determining whether an image is a logo or doesn't contain any important info or contains just few text. Your task is to classify the given image and respond with a simple 'Yes' or 'No'. "
            "Provide only the answer and strictly adhere to the output format specified below. No additional text, explanations, or extra information should be provided.\n\n"
            "Output Format (in JSON):\n"
            "{\n"
            "  'is_logo': 'Yes' or 'No'\n"
            "}\n\n"
            "Guidelines:\n"
            "- Respond only with 'Yes' or 'No' based on whether the image is a logo or doesnt contain any important info or contains just few text.\n"
            "- Use the exact output format shown above, including the key 'is_logo' and either 'Yes' or 'No' as the value.\n"
            "- Do not add any extra words, comments, or explanations outside of the given format."
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Call the vision agent with the role and image path
                is_logo_response = self.ollama_vision_agent(role_1, img_path)

                # Validate and parse the JSON response
                is_logo_json = json.loads(is_logo_response)

                # Ensure the response contains the required key
                if "is_logo" in is_logo_json and is_logo_json["is_logo"] in ["Yes", "No"]:
                    return is_logo_json["is_logo"] == "Yes"
                else:
                    raise ValueError("Invalid JSON structure or missing 'is_logo' key.")
            
            except json.JSONDecodeError:
                self.logger.error(f"Attempt {attempt + 1}: Response is not valid JSON: {is_logo_response}")
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: Error during classification: {e}")
            
            # Retry after a short delay if an error occurs
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                self.logger.error("Image classification failed after multiple attempts. Hence classifying it as logo.")
                return True

        # Default return in case all retries fail (though this line is unlikely to be reached due to raise)
        return False

    def extract_information_multiple_times(self, img_path: str, attempts: int = 3) -> List[str]:
        
        role_2 = """You are a precise visual content analyzer specialized in extracting information from images. Your task is to methodically identify, analyze, and structure information from images containing text, tables, graphs, and/or flowcharts.

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

        Remember: Accuracy and precision are paramount. Output only what you can see with absolute certainty."""


        results = []
    
        for response_index in range(3):  # Collect 3 responses
            for attempt in range(attempts):
                try:
                    # Call the vision agent
                    result = self.ollama_vision_agent(role_2, img_path)
                    results.append(result.strip())
                    break                        
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} for Response {response_index + 1}: Failed with error: {e}")
                    if attempt == attempts - 1:
                        error_msg = f"Failed to generate Response {response_index + 1} after {attempts} attempts: {e}"
                        results.append(error_msg)
                        self.logger.error(error_msg)
                
                time.sleep(1)  # Delay before retrying
        
        return results


    def determine_best_response(self, responses: List[str], img_path: str) -> int:

        concatenated_responses = "\n\n".join([f"Response {i+1}:\n{resp}" for i, resp in enumerate(responses)])
        role_3 = (
            "You are a QA evaluator. I have three responses for the same task, and your job is to determine which one is the best. "
            "The responses might vary slightly, but you must select the most complete and accurate one based on the content extracted from the image. "
            f"Responses:\n{concatenated_responses}\n\n"
            "Respond with just the number: 1, 2, or 3. No additional text, explanation, or formatting is needed.\n"
            "Output Format (strictly):\n"
            "The correct answer is: [1, 2, or 3]"
            "Example Response : "
            "The correct answer is: 2"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Call the vision agent with the role and image path
                response = self.ollama_vision_agent(role_3, img_path)

                # Parse and validate the response
                if "The correct answer is:" in response:
                    answer = int(response.split("The correct answer is:")[1].strip()[0])

                    if answer in [1, 2, 3]:
                        return answer
                    else:
                        raise ValueError("Response contains an invalid number.")
                else:
                    raise ValueError("Response does not follow the required format.")

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: QA evaluator failed with error: {e}")
            
            # Retry after a short delay if an error occurs
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise RuntimeError("QA evaluation failed after multiple attempts.")
            

    def translate_response_to_original_language(self, response: str, img_path: str) -> str:
        language = "German"
        role_4 = (
            f"You are a translator. Your job is to translate the text into {language}. "
            "Provide only the translated text with no additional comments, explanations, or formatting.\n\n"
            "Text to be translated:\n"
            f"{response}\n\n"
            "Output Format:\n"
            "[Translated text in the target language]"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Call the translation agent
                translated_response = self.ollama_vision_agent(role_4, img_path)

                # Perform basic validation: ensure no extra text or formatting
                if translated_response.strip():
                    return translated_response.strip()
                else:
                    raise ValueError("Empty or invalid translation response.")

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: Translation failed with error: {e}")
            
            # Retry after a short delay if an error occurs
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise RuntimeError("Translation failed after multiple attempts.")


    def ollama_vision_agent(self, role: str, img_path: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[{
                'role': 'user',
                'content': role,
                'images': [img_path]
            }]
        )
        return response['message']['content']

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

        for result in self.results:
            if result["contains_info"]:
                # Add extracted info as a comment below the image reference in Markdown
                image_ref = f"![{result['image']}]({result['image']})"
                extracted_info = result['extracted_info']
                if extracted_info.find("**Entnommene Informationen**") != -1:
                    extracted_info = extracted_info.split("**Entnommene Informationen**")[1].strip()
                elif extracted_info.find("**Extracted Information**") != -1:
                    extracted_info = extracted_info.split("**Extracted Information**")[1].strip()
                else:
                    extracted_info = extracted_info
                extracted_info_comment = f"\n ## Extracted Info of {result['image_path']}: \n{extracted_info}"
                content = content.replace(image_ref, extracted_info_comment)
            else:
                image_ref = f"![{result['image']}]({result['image']})"
                content = content.replace(image_ref, "")

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
            self.logger.info(f"Image Path: {result['image_path']}")
            self.logger.info(f"  - Is Logo: {result['is_logo']}")
            self.logger.info(f"  - Contains Info: {result['contains_info']}")
            self.logger.info(f"  - Extracted Info: {result['extracted_info']}")


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

    logger = logging.getLogger("RevParser")

    # Create an instance of ImageProcessor
    processor = ImageProcessor(args.folder, args.model, logger)

    # Process images
    processor.process_images()

    # Update Markdown file with extracted info
    processor.update_markdown()

    # Print summary of results
    processor.summarize_results()
