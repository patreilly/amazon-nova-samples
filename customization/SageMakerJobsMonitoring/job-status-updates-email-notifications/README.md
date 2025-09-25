# SageMaker Training Job & HyperPod Job Status Email Notifications
This tool helps a user enable job status email notifications for their SageMaker Training Jobs (TJ) and HyperPod (HP) jobs. 
When a job's status gets changed from running to succeeded/failed, an email notification will be sent to the user's chosen email address(es). 
## Prerequisites:
### General: 
- boto3: Run ```pip install boto3```
### HyperPod-Specific: 
- **Amazon CloudWatch Observability** must be installed on the EKS cluster running your HP jobs: This enables Container Insights logs to be generated. Information on how to install the add-on can be found [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Observability-EKS-addon.html). 
## Usage:
Make sure you've refreshed your AWS credentials before running the below command. If you want to check the parameters to use, run the following command:
```
python enable_sagemaker_job_notifs.py --help
```
### Basic Usage
```
python enable_sagemaker_job_notifs.py --email [EMAIL(S) HERE] --region [REGION HERE] --platform [SMTJ or SMHP] --rate [# MINUTES]
```
### Example Usage:
```
python enable_sagemaker_job_notifs.py --email test@amazon.com test2@gmail.com --region us-east-1 --platform SMHP --rate 15
```
### Steps:
1. Run the above command, replacing the different parameters with your associated values.
2. Check CloudFormation in the AWS Console to make sure the stack creation succeeds and all the resources are deployed to your AWS account. 
3. After the stack is fully deployed, check your email(s) and confirm the subscription so you can receive email notifications when a job is completed. 
![An image displaying the subscription email the user will receive upon stack completion.](../imgs/job_subscription_example.png)
4. Once your TJ or HP job completes, you should get a notification to your email that looks similar to the below image. Each job entry in the email should contain: the job name, the updated status, timestamp that the event occurred. 
![An image displaying an example of a job notification email that the user will receive when a job completes.](../imgs/job_notification_example.png)
### Parameters:
- **Email:** Include 1+ email that you want job notifications to go to, separated by a space between each email.  
- **Region:** Pick the region that you're deploying your jobs in (e.g. us-east-2). 
- **Platform:** Pick either SageMaker Training Job (SMTJ) updates or SageMaker HyperPod updates (SMHP).
- **Rate:** Only applicable for SageMaker HyperPod job notifications. This is the rate (in minutes) in which an EventBridge rule will be triggered to check if any job statuses have updated. 
## Disclaimers
* Container Insights logs (which are included as a part of the Amazon CloudWatch Observability add-on) are required to monitor HyperPod job statuses. 
  * As such, if these logs stop being created for any reason (e.g. add-on isn't updated), the HyperPod job notifications won't work.  
* The job status updates are only reported in UTC. 