import boto3
import argparse
import sys
import os
import time
import re

ALLOWED_PLATFORMS = ['SMTJ', 'SMHP']

def wait_for_resources_to_generate(cf_client, stack_name):
     print("Creating resources...", end="", flush=True)
     while True:
        response = cf_client.describe_stacks(StackName=stack_name)
        status = response['Stacks'][0]['StackStatus']

        if status == 'CREATE_COMPLETE':
            print("\nResources created!")
            break
        elif status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED']:
            print(f"\nResource creation failed with status: {status}")
            sys.exit(1)

        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)

def validate_region_format(region):
    pattern = r"^[a-z]+-[a-z]+-\d+$"
    if not re.match(pattern, region):
        raise argparse.ArgumentTypeError(
            f"Invalid region: {region}. The correct format should be similar to us-east-1."
        )
    return region

def main():
    parser = argparse.ArgumentParser(
        description="Create AWS infrastructure for Nova customization job notifications"
    )
    parser.add_argument(
        "--email",
        required=True,
        nargs="+",
        help="The email address(es) to receive job notifications. If there are multiple emails, separate them by a singular space (e.g. --email email1@domain.com email2@domain.com)."
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        type=validate_region_format,
        help="The AWS region to deploy the resources in (e.g. us-east-1)."
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=ALLOWED_PLATFORMS,
        help="The SageMaker platform to monitor jobs for (Choose from the options: SMTJ, SMHP)."
    )
    parser.add_argument(
         "--rate",
         type=int,
         default=15,
         required=False,
         help="The number of minutes between each query for job status updates (default: 15). Email notifications will only be sent if a job update has occurred within the last query period. This parameter only affects SMHP job status updates."
    )
    args = parser.parse_args()

    # Load CloudFormation template based on user input for SMTJ or SMHP
    if(args.platform == "SMTJ"):
        template_file = os.path.join(os.path.dirname(__file__), "tj_job_notification_template.yaml")
    else:
        template_file = os.path.join(os.path.dirname(__file__), "hp_job_notification_template.yaml")

    try:
        with open(template_file, "r") as f:
            template_body = f.read()
    except Exception as e:
        print(f"Error reading template file: {e}")
        sys.exit(1)

    cf_client = boto3.client("cloudformation", region_name=args.region)
    stack_name = f"{args.platform}-job-notifications-{args.region}"

    # Create CloudFormation stack of resources needed for job tracking
    try:
        if(args.platform == "SMTJ"):
            response = cf_client.create_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=[
                            {
                                "ParameterKey": "EmailAddress",
                                "ParameterValue": ",".join(args.email)
                            }
                        ],
                        Capabilities=["CAPABILITY_NAMED_IAM"]
            )
        else:
            response = cf_client.create_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=[
                            {
                                "ParameterKey": "EmailAddress",
                                "ParameterValue": ",".join(args.email)
                            },
                            {
                                "ParameterKey": "Rate",
                                "ParameterValue": str(args.rate)
                            }
                        ],
                        Capabilities=["CAPABILITY_NAMED_IAM"]
                    )

        # Wait for resources to generate
        wait_for_resources_to_generate(cf_client, stack_name)

        print("You must check your email to confirm your subscription for receiving Nova customization job status updates!")
        print("You'll receive the confirmation email within a few minutes.")

    except cf_client.exceptions.AlreadyExistsException:
        print(f"Stack {stack_name} already exists.")
    except Exception as e:
        print("Error creating resources:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()