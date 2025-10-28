import base64
import json
from datetime import datetime

import numpy as np


def cosine_sim(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    magnitude_vector1 = np.linalg.norm(vector1)
    magnitude_vector2 = np.linalg.norm(vector2)

    if magnitude_vector1 == 0 or magnitude_vector2 == 0:
        return 0  # Handle cases where one or both vectors are zero vectors

    cosine_similarity = dot_product / (magnitude_vector1 * magnitude_vector2)
    return cosine_similarity


def load_file_as_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def pretty_format(obj, indent=2):
    obj_json_safe = convert_datetime(obj)
    return json.dumps(obj_json_safe, indent=indent)
