# SageMaker Job Monitoring
This folder features a collection of observability scripts sourrounding Sagemaker HyerPod and Training Jobs. Please
visit any of the below links to see instructions for using each of the scripts

- [SageMaker Training Job & HyperPod Job Status Email Notifications](#sagemaker-training-job--hyperpod-job-status-email-notifications)
- [SageMaker Training Job & HyperPod Nova Customization job training estimates](#sagemaker-training-job--hyperpod-nova-customization-training-job-estimates)

## SageMaker Training Job & HyperPod Job Status Email Notifications
This tool helps a user enable job status email notifications for their SageMaker Training Jobs (TJ) and HyperPod (HP) jobs. 
When a job's status gets changed from running to succeeded/failed, an email notification will be sent to the user's chosen email address(es). 
### Prerequisites:
#### General: 
- boto3: Run ```pip install boto3```
#### HyperPod-Specific: 
- **Amazon CloudWatch Observability** must be installed on the EKS cluster running your HP jobs: This enables Container Insights logs to be generated. Information on how to install the add-on can be found [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Observability-EKS-addon.html). 
### Usage:
Make sure you've refreshed your AWS credentials before running the below command. If you want to check the parameters to use, run the following command:
```
python enable_sagemaker_job_notifs.py --help
```
#### Basic Usage
```
python enable_sagemaker_job_notifs.py --email [EMAIL(S) HERE] --region [REGION HERE] --platform [SMTJ or SMHP] --rate [# MINUTES]
```
#### Example Usage:
```
python enable_sagemaker_job_notifs.py --email test@amazon.com test2@gmail.com --region us-east-1 --platform SMHP --rate 15
```
#### Steps:
1. Run the above command, replacing the different parameters with your associated values.
2. After the stack is fully deployed, check your email(s) and confirm the subscription so you can receive email notifications when a job is completed. 
![An image displaying the subscription email the user will receive upon stack completion.](../SageMakerJobsMonitoring/imgs/job_subscription_example.png)
3. Once your TJ or HP job completes, you should get a notification to your email that looks similar to the below image. Each job entry in the email should contain: the job name, the updated status, timestamp that the event occurred. 
![An image displaying an example of a job notification email that the user will receive when a job completes.](../SageMakerJobsMonitoring/imgs/job_notification_example.png)
#### Parameters:
- **Email:** Include 1+ email that you want job notifications to go to, separated by a space between each email.  
- **Region:** Pick the region that you're deploying your jobs in (e.g. us-east-2). 
- **Platform:** Pick either SageMaker Training Job (SMTJ) updates or SageMaker HyperPod updates (SMHP).
- **Rate:** Only applicable for SageMaker HyperPod job notifications. This is the rate (in minutes) in which an EventBridge rule will be triggered to check if any job statuses have updated. 
### Disclaimers
* Container Insights logs (which are included as a part of the Amazon CloudWatch Observability add-on) are required to monitor HyperPod job statuses. 
  * As such, if these logs stop being created for any reason (e.g. add-on isn't updated), the HyperPod job notifications won't work.  
* The job status updates are only reported in UTC. 

## SageMaker Training Job & HyperPod Nova customization training job estimates

This script can be used to estimate training times for CPT/PPO/SFT/DPO Nova Customization training
jobs on both Sagemaker HyperPod and SageMaker Training Jobs.

### Prerequisites:
Ensure that you have access to the recipe that you plan on using for your training job. This recipe should be similar to 
this sample recipe below:

```
## Run config
run:
  name: "my-cpt-run"             
  model_type: "amazon.nova-micro-v1:0:128k"  
  model_name_or_path: "nova-micro/prod"
  replicas: 8                   
  data_s3_path: ""                
  output_s3_path: ""              

## Training specific configs
training_config:
  max_length: 8192               
  global_batch_size: 256           

  trainer:
    max_epochs: 1               

  model:
    hidden_dropout: 0.0          
    attention_dropout: 0.0       
    ffn_dropout: 0.0             

    optim:
      lr: 1e-5                 
      name: distributed_fused_adam 
      adam_w_mode: true       
      eps: 1e-06               
      weight_decay: 0.0        
      betas:                   
        - 0.9
        - 0.999
      sched:
        warmup_steps: 10     
        constant_steps: 0    
        min_lr: 1e-6         
```

### Usage:
Run the script by using a command similar to: 
``` python get_training_time_estimate.py ```

### Example Execution:
```
% python3 get_training_time_estimate.py

Select training type:
1. cpt
2. ppo
3. sft
4. dpo
Enter the number of your choice: 1
Select model type:
1. nova-micro
2. nova-lite
3. nova-pro
Enter the number of your choice: 3
Enter path to YAML file: test-recipe.yaml
Enter dataset sample size (press Enter to use default 100,000): 100000

Estimated training time (cpt, nova-pro, 8 P5s, 256 GBS, 8192 max_length): 1 days 6 hours

Please note that these estimates are approximate projections and should not be interpreted as definitive training 
durations. Please monitor CloudWatch logs for more accurate progress and estimates.
```

Simply walk through the prompts to receive your training time estimate. Please note that these estimates
are approximate projections and should not be interpreted as definitive training durations. Actual training
times may vary significantly based on multiple factors. For more accurate estimates, please check CloudWatch
logs while your training job is running.