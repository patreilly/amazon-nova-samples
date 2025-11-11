# QA testing using Amazon Nova Act


This project demonstrates agentic quality assurance (QA) automation using Amazon Bedrock AgentCore Browser and Amazon Nova Act. It showcases how AI-powered testing agents can automatically validate web applications through intelligent browser interactions, replacing traditional manual testing processes with scalable, automated solutions.

## Overview

This demonstration implements a complete agentic QA workflow for a mock retail web application, showing how organizations can transform their testing processes from manual operations to automated, AI-driven validation systems.

### Key Benefits

- **80% Reduction in Manual Testing**: Automated validation of critical user journeys
- **Comprehensive Coverage**: AI-generated tests cover edge cases often missed in manual testing
- **Scalable Architecture**: Parallel execution reduces testing time from hours to minutes
- **Enterprise-Ready**: Built on AWS infrastructure with proper security and resource management

## Architecture

The demo consists of three main components:

1. **Sample Retail Web Application**: A fully functional e-commerce site with product catalog, search, filtering, and user interactions
2. **AI Test Generation**: Automated creation of test cases using Amazon Kiro or Amazon Q CLI
3. **Agentic Test Execution**: Amazon Nova Act agents performing tests through Amazon Bedrock AgentCore Browser

## Prerequisites
Before deploying this demo, ensure you have:
### AWS Requirements
- **AWS CLI configured** with appropriate permissions
- **AWS account** with access to Amazon Bedrock AgentCore Browser, CloudFormation, CloudFront, and S3
- **IAM permissions** for creating and managing AWS resources

### Development Environment
- **Python 3.11 or higher**
- **Node.js 18+ and npm**
- **jq** (for JSON parsing in deployment scripts)

### API Access
- **Amazon Nova Act API Key** - Visit [Nova Act home page](https://nova.amazon.com/act) to generate your API key

## Getting Started

Follow these three main steps to deploy and test the application:

### Step 1: Deploy Infrastructure

First, configure your AWS CLI and deploy the complete infrastructure:

```bash
# Clone the repository
git clone <repository-url>
cd qa-testing-acbt-nova-act

# Configure AWS CLI (if not already done)
aws configure

# Navigate to scripts directory and deploy
cd scripts
./deployment.sh
```

**What this script does:**
- Creates CloudFormation stack with S3 bucket and CloudFront distribution
- Uploads all web application files to S3
- Configures security settings and permissions
- Provides the final application URL

After deployment completes, you'll receive:
- **Website URL**: Your deployed application URL
- **S3 Bucket Name**: Where files are stored
- **CloudFront Distribution ID**: For cache management

### Step 2: Generate Test Cases

Use Amazon Kiro or Amazon Q CLI to analyze the deployed application and generate comprehensive test cases:

**Option A: Using Amazon Kiro**
1. Open Amazon Kiro
2. Use the prompt: `"Analyze the QA testing demo application and create comprehensive test cases"`
3. Kiro will generate test scenarios covering all major functionality

![Kiro Test Generation Demo](assets/Kiro.gif)
*Amazon Kiro analyzing the application and generating comprehensive QA test cases*

**Option B: Using Amazon Q CLI**
```bash
# Use Amazon Q CLI to analyze and generate test cases
q "Analyze this web application and create comprehensive QA test cases"
```

**Sample test cases are already included** in the `qa-test-cases/` directory for reference.

### Step 3: Run Pytest

Execute the AI-generated tests using the pytest framework:

```bash
# Navigate to tests directory
cd tests

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install .

# Configure environment
cp .env.sample .env
# Edit .env with your deployed application URL and Nova Act API key

# Copy test cases to working directory
src/test_data/

# Run tests
pytest -v

# View HTML report
open reports/report.html
```

![Pytest Execution Demo](assets/pytest.gif)
*Pytest running the AI-generated test cases with Amazon Nova Act agents*

## Test Framework Features

- **AI-Powered Execution**: Tests executed by Amazon Nova Act agents that understand web interfaces
- **Parallel Processing**: Multiple tests run simultaneously in isolated browser sessions
- **Rich Reporting**: HTML reports include screenshots, logs, and execution details
- **JSON-Based**: No coding required - write tests in simple JSON format

### Writing Custom Tests

Tests are written in JSON format. Example test case:

```json
{
  "testId": "QA-01",
  "testName": "Homepage Load Test",
  "description": "Verify that the home page loads correctly",
  "testSteps": [
    {
      "expectedResult": "Home page loads successfully"
    },
    {
      "expectedResult": "Page title contains 'QA Test App'"
    },
    {
      "action": "Click on the search bar",
      "expectedResult": "Search bar is focused and ready for input"
    }
  ]
}
```

## Project Structure

```
qa-testing-acbt-nova-act/
├── README.md                    # This file
├── cloudformation-template.yaml # AWS infrastructure template
├── index.html                  # Main application file
├── app.js                      # Application logic
├── styles.css                  # Application styling
├── package.json                # Dependencies
├── images/                     # Product images
├── assets/                     # Documentation assets
├── qa-test-cases/              # Sample AI-generated test cases
├── scripts/                    # Deployment scripts
│   ├── deployment.sh           # Complete deployment
│   ├── update-stack.sh         # Update existing stack
│   └── README.md               # Script documentation
└── tests/                      # Test framework
    ├── README.md               # Detailed test documentation
    ├── pyproject.toml          # Python dependencies
    └── src/test_data/          # Working test cases directory
```

## Deployment Scripts

### `deployment.sh` - Complete Deployment
- **Use for**: First-time deployment or complete recreation
- **Creates**: New CloudFormation stack and uploads all files
- **Time**: ~10-15 minutes

### `update-stack.sh` - Safe Updates
- **Use for**: Updating CloudFormation template or configuration
- **Updates**: Infrastructure only (files not re-uploaded)
- **Time**: ~5-10 minutes

## Troubleshooting

### Common Issues

1. **Script Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **AWS CLI Not Configured**
   ```bash
   aws configure
   ```

3. **Missing jq Command**
   ```bash
   # macOS: brew install jq
   # Ubuntu: sudo apt-get install jq
   ```

4. **Application Not Loading**
   - Wait 10-15 minutes for CloudFront distribution deployment
   - Verify you're using the CloudFront URL (not S3 URL)

## Cost Considerations

- **S3 Storage**: ~$0.01/month for static files
- **CloudFront**: Free tier includes 1TB data transfer
- **Bedrock AgentCore Browser**: Pay-per-use during testing

## Additional Resources

- [Amazon Nova Act](https://nova.amazon.com/act)
- [Amazon Bedrock AgentCore Browser Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- [Scripts Documentation](scripts/README.md)
- [Tests Documentation](tests/README.md)
