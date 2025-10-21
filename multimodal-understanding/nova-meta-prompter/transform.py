"""
Amazon Nova Prompt Transformer

Simple API to align prompts with Amazon Nova guidelines.
"""

import os
import time
import glob
import boto3
from botocore.config import Config
from contextlib import contextmanager


# ============================================================================
# File utilities
# ============================================================================

def load_text_file(directory, filename):
    """Load a specific text file."""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()


def load_text_files(directory):
    """Load all text files from a directory into a dictionary."""
    files_dict = {}
    for filepath in glob.glob(os.path.join(directory, '*.txt')):
        filename = os.path.basename(filepath)
        filename_without_ext = os.path.splitext(filename)[0]
        with open(filepath, 'r', encoding='utf-8') as file:
            files_dict[filename_without_ext] = file.read()
    return files_dict


# ============================================================================
# Bedrock client utilities
# ============================================================================

def get_bedrock_client():
    """Create and configure a Bedrock client.

    Uses AWS_PROFILE environment variable if set.
    Region is automatically detected from AWS configuration.
    """
    config = Config(
        read_timeout=1000,
        max_pool_connections=1000
    )

    # AWS SDK automatically uses AWS_PROFILE and AWS_REGION env vars
    return boto3.client(
        service_name='bedrock-runtime',
        config=config
    )


@contextmanager
def bedrock_client_context():
    """Context manager for Bedrock client to ensure proper cleanup."""
    client = get_bedrock_client()
    try:
        yield client
    finally:
        client.close()


def bedrock_converse(bedrock_client, system_input, message, tool_list, model_id, inference_config=None):
    """Make a conversation request to Bedrock."""

    # Update tool choice if tools are provided
    if tool_list and 'tools' in tool_list and len(tool_list['tools']) > 0:
        tool_list.update({"toolChoice": {"tool": {"name": tool_list['tools'][0]['toolSpec']['name']}}})

    # Set default inference configuration if none provided
    if not inference_config:
        inference_config = {
            "maxTokens": 16000,
            # "temperature": 0.6,
            "topP": 0.4
        }

    try:
        response = bedrock_client.converse(
            modelId=model_id,
            system=[system_input],
            messages=[message],
            inferenceConfig=inference_config,
            toolConfig=tool_list
        )
        return response
    except bedrock_client.exceptions.ThrottlingException as e:
        wait_sec = 60
        print(f'LLM got throttled, waiting {str(wait_sec)} seconds.')
        # nosemgrep: arbitrary-sleep
        time.sleep(wait_sec)
        # Recursive retry
        return bedrock_converse(bedrock_client, system_input, message, tool_list, model_id, inference_config)


# ============================================================================
# Main transform function
# ============================================================================

def transform_prompt(prompt, model_id=None):
    """Transform any prompt to align with Amazon Nova guidelines.

    Args:
        prompt (str): The prompt to transform
        model_id (str, optional): Model to use for transformation. Defaults to Nova Premier.
            Options:
            - 'us.amazon.nova-premier-v1:0' (default)
            - 'global.anthropic.claude-sonnet-4-5-20250929-v1:0'

    Returns:
        dict: Dictionary containing:
            - thinking: Analysis of the transformation process
            - nova_draft: Initial transformed prompt
            - reflection: Reflection on the draft
            - nova_final: Final Nova-aligned prompt

    Environment Variables:
        AWS_PROFILE: AWS profile to use (optional, will use default if not set)
        AWS_REGION: AWS region (optional, will use default if not set)

    Example:
        >>> result = transform_prompt("Summarize this document: {document}")
        >>> print(result['nova_final'])
    """

    # Default to Nova Premier if no model specified
    if model_id is None:
        model_id = 'us.amazon.nova-premier-v1:0'

    # Load required prompt files
    system_prompt = load_text_file(os.path.join("data", "prompts"), "prompt_nova_migration_system.txt")
    prompt_template = load_text_file(os.path.join("data", "prompts"), "prompt_nova_migration.txt")
    migration_guidelines = load_text_file(os.path.join("data", "docs", "nova"), "migration_guidelines.txt")

    nova_docs = "\n".join(load_text_files(os.path.join("data", "nova", "general")).values())

    # Format the prompt
    formatted_prompt = prompt_template.format(
        nova_docs=nova_docs,
        migration_guidelines=migration_guidelines,
        current_prompt=prompt,
    )

    # Define the tool for structured output
    tool_list = {
        "tools": [
            {
                "toolSpec": {
                    "name": "convert_prompt",
                    "description": "Transforms any prompt to Nova-aligned format",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "thinking": {
                                    "type": "string",
                                    "description": "Detailed analysis of the transformation process including model-specific elements, relevant documentation, required optimizations, Nova compatibility considerations, and format adjustments",
                                },
                                "nova_draft": {
                                    "type": "string",
                                    "description": "The transformed Nova-aligned prompt following best practices",
                                },
                                "reflection": {
                                    "type": "string",
                                    "description": "Reflection on the draft prompt",
                                },
                                "nova_final": {
                                    "type": "string",
                                    "description": "Final Nova-aligned prompt based on reflections",
                                },
                            },
                            "required": [
                                "thinking",
                                "nova_draft",
                                "reflection",
                                "nova_final",
                            ],
                        }
                    },
                }
            }
        ]
    }

    system_message = {"text": system_prompt}
    message = {
        "role": "user",
        "content": [{"text": formatted_prompt}],
    }

    # Execute the transformation
    with bedrock_client_context() as client:
        response = bedrock_converse(client, system_message, message, tool_list, model_id)

    return response["output"]["message"]["content"][0]["toolUse"]["input"]


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    # Example with default Nova Premier model
    current_prompt = "Summarize this document: {MY_DOCUMENT}"
    result = transform_prompt(current_prompt)
    print("=" * 80)
    print("FINAL NOVA-ALIGNED PROMPT:")
    print("=" * 80)
    print(result['nova_final'])
