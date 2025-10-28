This is a collection of Jupyter Notebooks that will help you explore the capabilities and syntax of the Amazon Nova Embeddings model. There are just a few setup steps you need to follow before using the sample code provided in these notebooks.

## Prerequisites

Ensure you have met the following requirements before continuing.
- Python 3 is installed
- [AWS CLI](https://aws.amazon.com/cli/) is installed
- AWS CLI is [configured with IAM credentials](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html)


## Configure IAM Permissions

Ensure the IAM role you are using has been given the following permissions:

* bedrock:InvokeModel
* s3:PutObject

## Enable the Nova Embeddings Model in the Amazon Bedrock Console

Before you can make API requests to the Nova Embeddings model, you need to enable the model in your account using the Amazon Bedrock console. Follow [the instructions here](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html) to enable the model called "Amazon > Nova Multimodal Embeddings".

## Install Dependencies

We recommend using a Python virtual environment when running this code. Follow these steps to create a virtual environment.

1. Navigate to folder:
```bash
cd path/to/amazon-nova-embeddings-beta
```

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Activate virtual environment:
- On Windows:
```bash
.venv\Scripts\activate
```
- On macOS/Linux:
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. We've provided a convenience script that will convert PDF documents to images. That script has dependencies that should be installed by following [these instructions](https://github.com/Belval/pdf2image).

## Running the Notebooks

Jupyter Notebooks can be run in a number of ways. Choose the method you prefer from the following options.

### Microsoft VS Code

[Microsoft VS Code](https://code.visualstudio.com/) has great support for Jupyter Notebooks with a very user-friendly UI. Just install the ["Jupyter" extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) installed. After launching VS Code, choose **"Open Folder..."** and open this *"amazon-nova-embeddings-beta"* folder.

### From the Command Line

The setup steps above installed the command line version of Jupyter Notebook server. To use this option, do the following from the command line:

```
cd path/to/amazon-nova-embeddings-beta
```
```
source .venv/bin/activate
```
```
jupyter notebook
```

This will automatically open a browser-based UI that you can use to run the notebooks.

### Use Amazon SageMaker Notebooks

[Amazon SageMaker Notebooks](https://aws.amazon.com/sagemaker/ai/notebooks/) offers a way to run Jupyter Notebooks in the cloud. If you choose this option, you will need to edit the permissions of the SageMaker IAM role allow it access to Bedrock and S3 as described in the [Configure IAM Permissions](#configure-iam-permissions) section.