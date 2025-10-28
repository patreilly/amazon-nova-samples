import functools
import json
import os
import traceback
from datetime import datetime

import boto3

from utils.instrumentation import save_bedrock_invocations

MODEL_ID = "amazon.nova-2-multimodal-embeddings-v1:0"
REGION = "us-east-1"


@save_bedrock_invocations()
def generate_embedding_sync(request_body, region_name=REGION):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name,
    )

    body_json = json.dumps(request_body, indent=2)

    try:
        # Invoke the Nova Embeddings model.
        response = bedrock_runtime.invoke_model(
            body=body_json,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json",
        )

        # Decode the response body.
        response_body = json.loads(response.get("body").read())
        response_metadata = response["ResponseMetadata"]

        return response_body, response_metadata

    except Exception as e:
        # You would typically add your own exception handling here.
        print(e)


@save_bedrock_invocations()
def generate_embedding_async(
    request_body, s3_destination_bucket, region_name=REGION
):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name,
    )

    try:
        # Invoke the Nova Embeddings model.
        response = bedrock_runtime.start_async_invoke(
            modelId=MODEL_ID,
            modelInput=request_body,
            outputDataConfig={
                "s3OutputDataConfig": {"s3Uri": f"s3://{s3_destination_bucket}"}
            },
        )

        invocation_arn = response.get("invocationArn")
        response_metadata = response["ResponseMetadata"]

        return invocation_arn, response_metadata

    except Exception as e:
        # You would typically add your own exception handling here.
        print(e)


def extract_embedding(response_body, index=0):
    return response_body.get("embeddings")[index].get("embedding")
