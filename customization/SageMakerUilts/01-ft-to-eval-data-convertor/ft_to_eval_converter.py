#!/usr/bin/env python3
"""
FT to Eval Data Converter

This script converts fine-tuning (FT) data format to evaluation (eval) data format.
It supports both local file paths and S3 paths.

Usage:
    python ft_to_eval_converter.py --input <input_path> --output <output_path>

Example:
    python ft_to_eval_converter.py --input data.jsonl --output eval_data.jsonl
    python ft_to_eval_converter.py --input s3://bucket/data.jsonl --output s3://bucket/eval_data.jsonl
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Union
import boto3
import botocore


def is_s3_path(path: str) -> bool:
    """Check if the path is an S3 path."""
    return path.startswith("s3://")


def parse_s3_path(s3_path: str) -> tuple:
    """Parse S3 path into bucket and key."""
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts[0]
    key = "/".join(path_parts[1:])
    return bucket, key


def read_jsonl_file(file_path: str) -> List[Dict[str, Any]]:
    """Read a JSONL file from local or S3 path."""
    if is_s3_path(file_path):
        bucket, key = parse_s3_path(file_path)
        s3_client = boto3.client('s3')
        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            return [json.loads(line) for line in content.strip().split('\n')]
        except botocore.exceptions.ClientError as e:
            print(f"Error reading from S3: {e}")
            sys.exit(1)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [json.loads(line) for line in f]
        except Exception as e:
            print(f"Error reading local file: {e}")
            sys.exit(1)


def write_jsonl_file(data: List[Dict[str, Any]], file_path: str) -> None:
    """Write a JSONL file to local or S3 path."""
    jsonl_content = '\n'.join(json.dumps(item) for item in data)
    
    if is_s3_path(file_path):
        bucket, key = parse_s3_path(file_path)
        s3_client = boto3.client('s3')
        try:
            s3_client.put_object(
                Body=jsonl_content.encode('utf-8'),
                Bucket=bucket,
                Key=key
            )
            print(f"Successfully wrote to S3: {file_path}")
        except botocore.exceptions.ClientError as e:
            print(f"Error writing to S3: {e}")
            sys.exit(1)
    else:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(jsonl_content)
            print(f"Successfully wrote to local file: {file_path}")
        except Exception as e:
            print(f"Error writing to local file: {e}")
            sys.exit(1)


def convert_ft_to_eval(ft_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert FT data format to eval data format.
    
    FT format:
    {
        "system": [{"text": "system instruction"}],
        "messages": [
            {"role": "user", "content": [{"text": "user message"}]},
            {"role": "assistant", "content": [{"text": "assistant response"}]}
        ]
    }
    
    Eval format:
    {
        "system": "system instruction",
        "query": "user message",
        "response": "assistant response"
    }
    """
    eval_data = {}
    
    # Extract system instruction
    if "system" in ft_data and ft_data["system"] and "text" in ft_data["system"][0]:
        eval_data["system"] = ft_data["system"][0]["text"]
    else:
        eval_data["system"] = ""
    
    # Extract query (user message)
    eval_data["query"] = ""
    eval_data["response"] = ""
    
    if "messages" in ft_data:
        for message in ft_data["messages"]:
            if message["role"] == "user" and "content" in message:
                # Handle both string content and array of content objects
                if isinstance(message["content"], list):
                    # Extract text from content objects
                    content_texts = []
                    for content_item in message["content"]:
                        if isinstance(content_item, dict) and "text" in content_item:
                            content_texts.append(content_item["text"])
                    eval_data["query"] = "\n".join(content_texts)
                else:
                    eval_data["query"] = message["content"]
            
            elif message["role"] == "assistant" and "content" in message:
                # Handle both string content and array of content objects
                if isinstance(message["content"], list):
                    # Extract text from content objects
                    content_texts = []
                    for content_item in message["content"]:
                        if isinstance(content_item, dict) and "text" in content_item:
                            content_texts.append(content_item["text"])
                    eval_data["response"] = "\n".join(content_texts)
                else:
                    eval_data["response"] = message["content"]
    
    return eval_data


def main():
    parser = argparse.ArgumentParser(description='Convert FT data format to eval data format')
    parser.add_argument('--input', required=True, help='Input JSONL file path (local or S3)')
    parser.add_argument('--output', required=True, help='Output JSONL file path (local or S3)')
    args = parser.parse_args()
    
    print(f"Reading from: {args.input}")
    ft_data_list = read_jsonl_file(args.input)
    
    eval_data_list = []
    for i, ft_data in enumerate(ft_data_list):
        try:
            eval_data = convert_ft_to_eval(ft_data)
            eval_data_list.append(eval_data)
        except Exception as e:
            print(f"Error converting item {i}: {e}")
    
    print(f"Writing to: {args.output}")
    write_jsonl_file(eval_data_list, args.output)
    
    print(f"Conversion complete. Converted {len(eval_data_list)} items.")


if __name__ == "__main__":
    main()
