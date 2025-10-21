from datetime import datetime, timezone
import argparse
import boto3
import json
import re
import subprocess
import sys
import time

class SageMakerHyperPodStatusChecker:
    def __init__(self, cluster_name: str, job_name: str, namespace: str, region: str, num_dataset_samples: int, num_epochs: int, batch_size: int):
        """
        Args:
            cluster_name (str): The name of the SageMaker HyperPod cluster.
            job_name (str): The job name within the HyperPod cluster.
            namespace (str): The Kubernetes namespace that your job is running within.
            region (str): The AWS region.
            num_dataset_samples (int): The number of samples in the input dataset.
            num_epochs (int): The number of epochs used in your job.
            batch_size (int): The batch size used in your job.
        """
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)

        self.cluster_name = cluster_name
        self.cluster_id = self.get_cluster_id()
        self.job_name = job_name
        self.namespace = namespace
        self.region = region
        self.num_dataset_samples = num_dataset_samples
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.log_group_name = f"/aws/sagemaker/Clusters/{cluster_name}/{self.cluster_id}"
        self.log_stream_prefix = "SagemakerHyperPodTrainingJob/rig-group/"

    def get_cluster_id(self) -> str:
        """
        Get the HyperPod cluster ID for the given HyperPod cluster name.

        Returns:
            str: The HyperPod cluster ID.

        Raises:
            Exception: If the HyperPod cluster is not found.
        """
        try:
            response = self.sagemaker_client.list_clusters(NameContains=self.cluster_name)
            cluster_arn = response['ClusterSummaries'][0]['ClusterArn']
            return cluster_arn.split('/')[-1]
        except Exception:
            raise Exception(f"Cluster {self.cluster_name} not found")

    def connect_to_cluster(self):
        """
        Connect to the HyperPod cluster via the HyperPod CLI.
        """
        command = ['hyperpod', 'connect-cluster', '--cluster-name', self.cluster_name, '--region', self.region, '--namespace', self.namespace]

        try:
            subprocess.run(command, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("Unable to connect to HyperPod cluster: ", e.stderr)
            sys.exit(1)

    def get_job(self) -> any:
        """
        Get the job details of the given HyperPod job.
        """
        command = ['hyperpod', 'get-job', '--job-name', self.job_name, '--namespace', self.namespace]

        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            error_message = str(e.stderr)
            if "Not Found (404)" in error_message:
                print(f"Job '{self.job_name}' was not found in namespace '{self.namespace}' of cluster '{self.cluster_name}'. Please verify the job details and try again.")
                sys.exit()
            else:
                print("Unable to fetch job details: ", e.stderr)
                sys.exit(1)

    def get_latest_state_details(self, states: any):
        """
        Get the most recent state details of the HyperPod job based on all state changes.
        Priority order for equal timestamps:
        2 - Failed or Succeeded
        1 - Any state except Created
        0 - Created

        ex. {'lastTransitionTime': '2025-09-24T17:13:29Z', 'lastUpdateTime': '2025-09-24T17:13:29Z', 'message': 'PyTorchJob my_job is running.', 'reason': 'PyTorchJobRunning', 'status': 'True', 'type': 'Running'}
        """
        def key_func(state):
            timestamp = datetime.strptime(state['lastTransitionTime'], '%Y-%m-%dT%H:%M:%SZ')
            if state['type'] in ['Failed', 'Succeeded']:
                priority = 2
            elif state['type'] == 'Created':
                priority = 0
            else:
                priority = 1
            return timestamp, priority

        return max(states, key=key_func)

    def is_only_one_job_running(self) -> bool:
        """
        Disclaimer: As of 9/30/25, HyperPod pushes logs to CloudWatch log streams based on the instance ID that is performing the training.
        If multiple HyperPod jobs are running in the same HyperPod cluster at the same time, it can be impossible to distinguish which logs pertain to which jobs.
        Given this limitation, this script will only provide training progress details if only 1 job is running.
        """
        command = ['hyperpod', 'list-jobs', '-A']

        try:
            result = json.loads(subprocess.run(command, check=True, text=True, capture_output=True).stdout)
            running_jobs = [job for job in result['jobs'] if job.get('State') == 'Running']

            if len(running_jobs) == 1:
                return True
            else:
                print("Due to limitations of how HyperPod publishes logs to CloudWatch, this script will only provide job progress details if there is only 1 HyperPod job in progress.")
                print(f"There are currently {len(running_jobs)} jobs that are running in HyperPod cluster '{self.cluster_name}'. Re-execute this script when only 1 job is running to get job progress information of that job.")
                print("Please view the README at https://github.com/aws-samples/amazon-nova-samples/blob/main/customization/SageMakerUilts/SageMakerJobsMonitoring/README.md for more details.")
                return False
        except subprocess.CalledProcessError as e:
            print("Unable to determine job progress: ", e.stderr)
            sys.exit(1)

    def wait_for_query_results(self, query_id: str, timeout: int = 120) -> dict:
        """
        Wait for the given CloudWatch Logs Insights query to finish.

        Args:
            query_id (str): The ID of the query.
            timeout (int, optional): The maximum time to wait for results in seconds. Defaults to 120.

        Returns:
            dict: The query results.

        Raises:s
            TimeoutError: If the query times out.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            result = self.logs_client.get_query_results(queryId=query_id)
            if result['status'] in ['Complete', 'Failed', 'Cancelled']:
                return result
            time.sleep(3)
        raise TimeoutError("Query timed out")

    def query_logs(self, start_time: int, end_time: int) -> dict:
        """
        Query CloudWatch logs using Logs Insights.

        Args:
            start_time (int): The start time for the query in Unix seconds.
            end_time (int): The end time for the query in Unix seconds.

        Returns:
            dict: The query results.
        """
        try:
            query = f"""
                fields @timestamp, @message
                | sort @timestamp desc
                | filter @logStream like '{self.log_stream_prefix}'
                | filter @message like /Epoch \\d+:/
                | filter @message not like '?, ?it'
                | limit 1
            """
            start_query_response = self.logs_client.start_query(
                logGroupName=self.log_group_name,
                startTime=start_time,
                endTime=end_time,
                queryString=query
            )

            query_id = start_query_response['queryId']
            response = self.wait_for_query_results(query_id)

            return response
        except Exception as e:
            print(f"Warning: Unable to determine job progress: {str(e)}")
            sys.exit(1)

    def handle_running_job(self, latest_state_details: any):
        """
        Parse CloudWatch logs to determine the training progress made for an in-progress HyperPod job.
        """
        # Query CloudWatch between when the job entered a 'Running' state, and the present time
        start_strptime = datetime.strptime(latest_state_details.get('lastTransitionTime'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        start_time = int(start_strptime.timestamp())
        end_time = int(datetime.now().timestamp())

        query_logs = self.query_logs(start_time, end_time)
        results = query_logs.get("results", [])

        if results:
            epoch_log = {col["field"]: col["value"] for col in results[0]}.get("@message")
            log_timestamp = {col["field"]: col["value"] for col in results[0]}.get("@timestamp")

            iterations_per_epoch = self.num_dataset_samples / self.batch_size
            total_iterations = iterations_per_epoch * self.num_epochs

            match = re.search(r'Epoch (\d+): : (\d+)it', epoch_log)
            if match:
                epoch = int(match.group(1))
                iteration = int(match.group(2))

                if iteration is None or epoch is None:
                    print(f"Training for job '{self.job_name}' is in progress, but there is not enough data "
                          f"to estimate progress as of {datetime.now(timezone.utc).strftime('%H:%M UTC %m/%d/%Y')}. Try again in a few minutes.")

                total_completed_iterations = (epoch * iterations_per_epoch) + iteration
                elapsed_time = (log_timestamp - start_time).total_seconds()
                progress_percentage = (total_completed_iterations / total_iterations) * 100

                if progress_percentage >= 100:
                    print (f"Training iterations for job '{self.job_name}' are complete. "
                            f"Final validation, fine-tuning, and artifact upload steps are in progress as of "
                            f"{log_timestamp.strftime('%H:%M UTC %m/%d/%Y')}.")
                elif progress_percentage <= 0:
                    print (f"Training for job '{self.job_name}' has just begun. Initial model setup and "
                        f"first training iterations are in progress as of "
                        f"{log_timestamp.strftime('%H:%M UTC %m/%d/%Y')}. Check back in a few minutes "
                        f"for a more detailed progress update.")

                time_per_iteration = elapsed_time / total_completed_iterations if total_completed_iterations > 0 else 0
                remaining_iterations = total_iterations - total_completed_iterations
                remaining_minutes = (remaining_iterations * time_per_iteration) / 60

                print (f"Training for job '{self.job_name}' is approximately {progress_percentage:.1f}% complete. "
                    f"Estimated training time remaining: {remaining_minutes:.1f} minutes "
                    f"[{remaining_minutes/60:.1f} hours]")

        else:
            print(f"Training for job '{self.job_name}' is in progress, but the job progress percentage could not be determined "
                  f"as of {datetime.now(timezone.utc).strftime('%H:%M UTC %m/%d/%Y')}. Please try again in a few minutes.")

    def process_job_states(self, job_details: any):
        """
        Determine the current HyperPod job state and then handle based on if it's in-progress or not.
        """
        try:
            all_state_details = job_details.get('Status', {}).get('conditions', [])
        except:
            print(f"Unable to determine job progress details of job '{self.job_name}'")
            sys.exit()

        if not all_state_details:
            print(f"Did not find any job status changes for job '{self.job_name}'. Please rerun this script once training begins to get a training time estimate.")
            sys.exit()

        latest_state_details = self.get_latest_state_details(all_state_details)
        latest_state = latest_state_details.get('type', '')
        latest_state_start_time = latest_state_details.get('lastTransitionTime')

        if latest_state == 'Created':
            print(f"Job '{self.job_name}' has been created, but training has not yet begun. Please rerun this script once training begins to get a training time estimate.")
            sys.exit()

        if latest_state == 'Succeeded':
            print(f"Job '{self.job_name}' succeeded at {latest_state_start_time}")
            sys.exit()

        if latest_state == 'Failed':
            failure_message = latest_state_details.get('message')
            if failure_message:
                print(f"Job '{self.job_name}' failed at {latest_state_start_time}. Kubernetes provided the following failure message: '{failure_message}'")
            else:
                print(f"Job '{self.job_name}' failed at {latest_state_start_time}.")
            sys.exit()

        if latest_state == 'Running':
            if self.is_only_one_job_running():
                print("Please note that these estimates are approximate projections and should not be interpreted as definitive training durations.\n")
                self.handle_running_job(latest_state_details)
            sys.exit()

        print(f"Job '{self.job_name}' reached status '{latest_state}' at {latest_state_start_time}")
        sys.exit()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Check SageMaker HyperPod job progress information for a given HyperPod cluster')
    parser.add_argument('--cluster-name',
                        required=True,
                        help='The name of the SageMaker HyperPod cluster where your job is running.')
    parser.add_argument('--job-name',
                        required=True,
                        help='The name of the job to check progress of.')
    parser.add_argument('--namespace',
                        required=True,
                        help='The Kubernetes namespace that your job is running in.')
    parser.add_argument('--region',
                        required=True,
                        help='The AWS region (ex. us-east-1).')
    parser.add_argument('--num-dataset-samples',
                        required=True,
                        type=int,
                        help='The approximate number of samples in your S3 training dataset.')
    parser.add_argument('--num-epochs',
                        required=True,
                        type=int,
                        help='Number of epochs of your job. You can find this value in your recipe YAML file as max_epochs.')
    parser.add_argument('--batch-size',
                        required=True,
                        type=int,
                        help='Batch size of your job. You can find this value in your recipe YAML file as global_batch_size.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    status_checker = SageMakerHyperPodStatusChecker(
        cluster_name=args.cluster_name,
        job_name=args.job_name,
        namespace=args.namespace,
        region=args.region,
        num_dataset_samples=args.num_dataset_samples,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size
    )
    status_checker.connect_to_cluster()
    job = status_checker.get_job()
    status_checker.process_job_states(job)


if __name__ == "__main__":
    main()

