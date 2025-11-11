import json
import os
import time
from datetime import datetime, timedelta, timezone

import boto3

REGION = "us-east-1"


def get_folder_name_for_job(invocation_job):
    invocation_arn = invocation_job["invocationArn"]
    invocation_id = invocation_arn.split("/")[-1]
    submit_time = invocation_job["submitTime"]
    timestamp = submit_time.astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{timestamp}_{invocation_id}"
    return folder_name


def is_job_output_downloaded(invocation_job, output_dir="output"):
    """
    This function checks if the output files for the given invocation job have been downloaded.
    """
    folder_name = get_folder_name_for_job(invocation_job)
    output_dir = os.path.abspath(f"{output_dir}/{folder_name}")
    # Determine if the folder is empty.
    files = os.listdir(output_dir)
    return len(files) > 0


def download_job_output(invocation_arn, bucket_name, destination_folder):
    """
    This function downloads the output files for the given invocation ARN.
    """
    invocation_id = invocation_arn.split("/")[-1]
    output_dir = os.path.abspath(os.path.join(destination_folder, "s3_contents"))

    # Ensure the output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Create an S3 client
    s3 = boto3.client("s3", region_name=REGION)

    # List objects in the specified folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=invocation_id)

    # Download all the files.
    print(f"Downloading output files for job {invocation_id}")
    contents = response.get("Contents", [])
    if len(contents) == 0:
        print(f"No output files found for job {invocation_id}")
        return
    for obj in contents:
        key = obj["Key"]
        file_name = os.path.basename(key)
        destination_path = os.path.join(output_dir, file_name)
        s3.download_file(bucket_name, key, destination_path)


def elapsed_time_for_invocation_job(invocation_job):
    """
    This function returns the elapsed time for the given invocation job.
    """
    invocation_start_time = invocation_job["submitTime"].timestamp()
    if "endTime" in invocation_job:
        invocation_end_time = invocation_job["endTime"].timestamp()
        elapsed_time = int(invocation_end_time - invocation_start_time)
    else:
        elapsed_time = int(time.time() - invocation_start_time)

    return elapsed_time


def download_recent_async_jobs(
    output_dir="output", hours=24, wait_for_running_jobs=True
):

    submit_time_after = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

    # Save failed jobs.
    failed_jobs_args = {"statusEquals": "Failed"}
    if submit_time_after is not None:
        failed_jobs_args["submitTimeAfter"] = submit_time_after

    failed_jobs = bedrock_runtime.list_async_invokes(**failed_jobs_args)

    for job in failed_jobs["asyncInvokeSummaries"]:
        save_failed_job(job)

    # Save completed jobs.
    completed_jobs_args = {"statusEquals": "Completed"}
    if submit_time_after is not None:
        completed_jobs_args["submitTimeAfter"] = submit_time_after

    completed_jobs = bedrock_runtime.list_async_invokes(**completed_jobs_args)

    for job in completed_jobs["asyncInvokeSummaries"]:
        save_completed_job(job)

    if wait_for_running_jobs:
        monitor_and_download_in_progress_async_jobs(output_dir=output_dir)


def monitor_and_download_in_progress_async_jobs(output_dir="output"):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

    invocation_list = bedrock_runtime.list_async_invokes(statusEquals="InProgress")
    in_progress_jobs = invocation_list["asyncInvokeSummaries"]

    pending_job_arns = [job["invocationArn"] for job in in_progress_jobs]

    print(f'Monitoring {len(pending_job_arns)} "InProgress" jobs.')

    while len(pending_job_arns) > 0:
        job_arns_to_remove = []
        for job_arn in pending_job_arns:
            # Get latest job status.
            job_update = bedrock_runtime.get_async_invoke(invocationArn=job_arn)
            status = job_update["status"]

            if status == "Completed":
                save_completed_job(job_update, output_dir=output_dir)
                job_arns_to_remove.append(job_arn)
            elif status == "Failed":
                save_failed_job(job_update, output_dir=output_dir)
                job_arns_to_remove.append(job_arn)
            else:
                job_id = get_job_id_from_arn(job_update["invocationArn"])
                elapsed_time = elapsed_time_for_invocation_job(job_update)
                minutes, seconds = divmod(elapsed_time, 60)
                # print(
                #     f"Job {job_id} is {status}. Elapsed time: {minutes}m, {seconds}s."
                # )
        for job_arn in job_arns_to_remove:
            pending_job_arns.remove(job_arn)

        time.sleep(1)

    print("Monitoring and download complete!")


def elapsed_time_for_invocation_arn(invocation_arn):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

    # Get the job details.
    invocation_job = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)

    return elapsed_time_for_invocation_job(invocation_job)


def elapsed_time_for_invocation_job(invocation_job):
    invocation_start_time = invocation_job["submitTime"].timestamp()
    if "endTime" in invocation_job:
        invocation_end_time = invocation_job["endTime"].timestamp()
        elapsed_time = int(invocation_end_time - invocation_start_time)
    else:
        elapsed_time = int(time.time() - invocation_start_time)

    return elapsed_time


def get_job_id_from_arn(invocation_arn):
    return invocation_arn.split("/")[-1]


def save_completed_job(job, output_dir="output"):
    job_id = get_job_id_from_arn(job["invocationArn"])
    job_duration = calculate_job_duration(job)
    job["durationSeconds"] = job_duration

    output_dir_abs = os.path.abspath(f"{output_dir}/{get_folder_name_for_job(job)}")

    # Ensure the output folder exists
    os.makedirs(output_dir_abs, exist_ok=True)

    status_file = os.path.join(output_dir_abs, "completed.json")

    if is_job_output_downloaded(job, output_dir=output_dir):
        print(f"Skipping completed job {job_id}. Output already downloaded.")
        return

    s3_bucket_name = (
        job["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
        .split("//")[1]
        .split("/")[0]
    )

    download_job_output(job["invocationArn"], s3_bucket_name, output_dir_abs)

    # Write the status file to disk as JSON.
    with open(status_file, "w") as f:
        json.dump(job, f, indent=2, default=str)


def save_failed_job(job, output_dir="output"):
    output_dir_abs = os.path.abspath(f"{output_dir}/{get_folder_name_for_job(job)}")
    output_file = os.path.join(output_dir_abs, "failed.json")

    job_id = get_job_id_from_arn(job["invocationArn"])

    # If the output file already exists, skip this job.
    if os.path.exists(output_file):
        print(f"Skipping failed job {job_id}, output file already exists.")
        return

    # Ensure the output folder exists
    os.makedirs(output_dir_abs, exist_ok=True)

    with open(output_file, "w") as f:
        print(f"Writing failed job {job_id} to {output_file}.")
        json.dump(job, f, indent=2, default=str)


def calculate_job_duration(job_data):
    # Parse the ISO format timestamps to datetime objects
    submit_time = job_data["submitTime"]
    end_time = job_data["endTime"]

    # Calculate the time difference
    duration = end_time - submit_time

    # Return total seconds
    return duration.total_seconds()
