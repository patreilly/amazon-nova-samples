#!/usr/bin/env python3

from random import randint
from amazon_image_gen import BedrockImageGenerator
import file_utils
import logging
import base64
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Set the image to be edited.
    source_image = "../images/amazon-coffee-maker-1.png"

    # Load the input image from disk.
    with open(source_image, "rb") as image_file:
        source_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Configure the inference parameters.
    inference_params = {
        "taskType": "OUTPAINTING",
        "outPaintingParams": {
            "image": source_image_base64,
            "text": "a coffee maker in a sparse stylish kitchen, a single plate of pastries next to the coffee maker, a single cup of coffee. highly detailed, highest quality, product imagery",  # Description of the background to generate
            "maskPrompt": "coffee maker",  # The element(s) to keep
            "outPaintingMode": "PRECISE",  # "DEFAULT" softens the mask. "PRECISE" keeps it sharp.
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # Number of variations to generate. 1 to 5.
            "quality": "standard",  # Allowed values are "standard" and "premium"
            "cfgScale": 7.0,  # How closely the prompt will be followed
            "seed": randint(0, 858993459),  # Use a random seed
        },
    }

    # Define an output directory with a unique name.
    generation_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_directory = f"output/{generation_id}"

    # Create the generator.
    generator = BedrockImageGenerator(
        output_directory=output_directory
    )

    # Generate the image(s).
    response = generator.generate_images(inference_params)

    if "images" in response:
        # Save each image
        file_utils.save_base64_images(response["images"], output_directory, "image")

if __name__ == "__main__":
    main()