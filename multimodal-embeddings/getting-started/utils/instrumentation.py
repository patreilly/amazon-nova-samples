import functools
import json
import os
import traceback
from datetime import datetime


def save_bedrock_invocations(output_dir="output"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_dir = os.path.join(output_dir, timestamp)
            os.makedirs(log_dir, exist_ok=True)

            # Log request parameters
            request_data = {"args": args, "kwargs": kwargs}
            with open(os.path.join(log_dir, f"{func.__name__}_input.json"), "w") as f:
                json.dump(request_data, f, indent=2, default=str)

            try:
                result = func(*args, **kwargs)
                # Log response
                with open(
                    os.path.join(log_dir, f"{func.__name__}_output.json"), "w"
                ) as f:
                    if func.__name__ == "generate_embedding_sync":
                        json.dump(
                            {"body": result[0], "ResponseMetadata": result[1]},
                            f,
                            indent=2,
                            default=str,
                        )
                    elif func.__name__ == "generate_embedding_async":
                        json.dump(
                            {"invocationArn": result[0], "ResponseMetadata": result[1]},
                            f,
                            indent=2,
                            default=str,
                        )
                return result
            except Exception as e:
                # Log exception
                exception_data = {
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "traceback": traceback.format_exc(),
                }
                with open(
                    os.path.join(log_dir, f"{func.__name__}_exception.json"), "w"
                ) as f:
                    json.dump(exception_data, f, indent=2)
                raise

        return wrapper

    return decorator
