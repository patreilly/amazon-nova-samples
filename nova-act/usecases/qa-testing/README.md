# Agentic QA Automation Demo: Retail Application Testing

This project demonstrates agentic quality assurance (QA) automation using Amazon Bedrock AgentCore Browser and Amazon Nova Act. It showcases how AI-powered testing agents can automatically validate web applications through intelligent browser interactions, replacing traditional manual testing processes with scalable, automated solutions.

## Use Case Overview

This demonstration implements a complete agentic QA workflow for a mock retail web application, illustrating how organizations can transform their testing processes from manual, time-intensive operations to automated, AI-driven validation systems.

### What This Demo Shows

- **AI-Generated Test Cases**: Automatic creation of comprehensive test scenarios by analyzing application code and functionality
- **Intelligent Test Execution**: AI agents that can understand web interfaces and perform complex user interactions
- **Parallel Test Processing**: Scalable execution across multiple isolated browser sessions
- **Enterprise Integration**: AWS-native architecture with proper resource management and reporting

### Key Benefits Demonstrated

- **80% Reduction in Manual Testing**: Automated validation of critical user journeys
- **Comprehensive Coverage**: AI-generated tests cover edge cases often missed in manual testing
- **Scalable Architecture**: Parallel execution reduces testing time from hours to minutes
- **Enterprise-Ready**: Built on AWS infrastructure with proper security and resource management

## Architecture Overview

The demo consists of three main components:

1. **Sample Retail Web Application**: A fully functional e-commerce site with product catalog, search, filtering, and user interactions
2. **AI Test Generation**: Automated creation of test cases using AI analysis of application features
3. **Agentic Test Execution**: Amazon Nova Act agents performing tests through Amazon Bedrock AgentCore Browser

## Prerequisites

Before deploying this demo, ensure you have:

### AWS Requirements
- **AWS CLI configured** with appropriate permissions
- **AWS account** with access to:
  - Amazon Bedrock AgentCore Browser
  - Amazon CloudFormation
  - Amazon CloudFront
  - Amazon S3
- **IAM permissions** for creating and managing AWS resources

### Development Environment
- **Python 3.11 or higher**
- **pip 23.0 or higher**
- **Node.js 18+ and npm** (for web application)
- **jq** (for JSON parsing in deployment scripts)
- **Operating System Support**:
  - macOS (Sierra or later)
  - Ubuntu (22.04 LTS or later)
  - Windows 10+ with WSL2

### API Access
- **Amazon Nova Act API Key**
  - Visit [Nova Act home page](https://nova.amazon.com/act) to generate your API key
  - Required for AI-powered test execution

## Deployment Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd qa-testing-acbt-nova-act
```

### Step 2: Deploy Complete Infrastructure

Use the automated deployment script that creates the CloudFormation stack and uploads all application files:

```bash
# Navigate to scripts directory
cd scripts

# Run the complete deployment script
./fix-deployment.sh
```

**What this script does:**
- Creates a CloudFormation stack with S3 bucket and CloudFront distribution
- Uploads all web application files to the S3 bucket
- Configures proper permissions and security settings
- Creates CloudFront invalidation for immediate availability
- Provides the final application URL

### Step 3: Verify Deployment

After the script completes, you'll receive:
- **S3 Bucket Name**: Where your files are stored
- **CloudFront Distribution ID**: For cache management
- **Website URL**: Your deployed application URL

Access the provided URL to verify:
- Homepage loads with product catalog
- Search functionality works
- Product filtering operates correctly
- Navigation between pages functions properly

### Alternative: Update Existing Deployment

If you need to update an existing deployment:

```bash
# Navigate to scripts directory
cd scripts

# Update existing stack (safer than recreating)
./update-stack.sh
```

## Writing and Running Tests

Once the web application is deployed and accessible, you can create and execute agentic QA tests using the Amazon Nova Act framework.

### Quick Test Setup

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
```

### Writing Tests

Tests are written in simple JSON format and stored in `tests/src/test_data/`. Each JSON file represents one test case:

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

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest -k "homepage"

# View HTML report
open reports/report.html
```

### Test Framework Features

- **AI-Powered Execution**: Tests are executed by Amazon Nova Act agents that understand web interfaces
- **Parallel Processing**: Multiple tests run simultaneously in isolated browser sessions
- **Rich Reporting**: HTML reports include screenshots, logs, and execution details
- **JSON-Based**: No coding required - write tests in simple JSON format

**For comprehensive documentation on test writing, execution, and advanced features, see the [Tests README](tests/README.md).**

The tests directory contains:
- Complete test framework setup instructions
- Detailed guide for writing JSON-based test cases
- Test execution and reporting documentation
- Advanced configuration options
- Troubleshooting guides

## Project Structure

```
qa-testing-acbt-nova-act/
├── README.md                    # This file - deployment and setup
├── cloudformation-simple.yaml  # AWS infrastructure template
├── package.json                # Web application dependencies
├── index.html                  # Main application file
├── app.js                      # Application logic
├── server.js                   # Local development server
├── styles.css                  # Application styling
├── images/                     # Product images
├── scripts/                    # Deployment automation scripts
│   ├── fix-deployment.sh       # Complete deployment (creates stack + uploads files)
│   ├── update-stack.sh         # Update existing stack
│   ├── invalidate-cloudfront.sh # Cache invalidation only
│   └── README.md               # Detailed script documentation
└── tests/                      # Test framework and execution
    ├── README.md               # Test writing and execution guide
    ├── pyproject.toml          # Python dependencies
    ├── conftest.py             # Test configuration
    └── src/                    # Test framework source code
```

## Deployment Scripts Reference

### `fix-deployment.sh` - Complete Deployment
- **Use when**: First-time deployment or complete recreation needed
- **What it does**: Deletes existing stack (if any), creates new stack, uploads files
- **Time**: ~10-15 minutes
- **Output**: Complete working application

### `update-stack.sh` - Safe Updates
- **Use when**: Updating CloudFormation template or configuration
- **What it does**: Creates change set, shows preview, applies updates
- **Time**: ~5-10 minutes
- **Output**: Updated infrastructure (files not re-uploaded)

### `invalidate-cloudfront.sh` - Cache Management
- **Use when**: Files changed but infrastructure unchanged
- **What it does**: Invalidates CloudFront cache only
- **Time**: ~1-2 minutes (effect takes 10-15 minutes)
- **Output**: Fresh cache for updated content

## Troubleshooting

### Common Deployment Issues

1. **Script Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **AWS CLI Not Configured**
   ```bash
   aws configure
   # Enter your AWS credentials and region
   ```

3. **Missing jq Command**
   ```bash
   # macOS
   brew install jq
   
   # Ubuntu/Debian
   sudo apt-get install jq
   
   # Windows (WSL)
   sudo apt-get install jq
   ```

4. **CloudFormation Stack Creation Fails**
   - Verify AWS credentials and permissions
   - Check region availability for required services
   - Ensure unique S3 bucket naming (script handles this automatically)

5. **Application Not Loading After Deployment**
   - Wait 10-15 minutes for CloudFront distribution to fully deploy
   - Check the provided URL is being accessed (not the S3 URL)
   - Verify files were uploaded correctly to S3

### Getting Help

- Review script output for specific error messages
- Check AWS CloudFormation console for stack events
- Verify CloudFront distribution status in AWS Console
- Consult the [Scripts README](scripts/README.md) for detailed script documentation
- Check the [Tests README](tests/README.md) for test-specific issues

## Cost Considerations

- **S3 Storage**: Minimal cost for static files (~$0.01/month)
- **CloudFront**: Free tier includes 1TB data transfer
- **CloudFormation**: No additional charges
- **Bedrock AgentCore Browser**: Pay-per-use during testing

## Additional Resources

- [Amazon Bedrock AgentCore Browser Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- [Amazon Nova Act](https://nova.amazon.com/act)
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)
- [Amazon CloudFront Developer Guide](https://docs.aws.amazon.com/cloudfront/)
- [Scripts Documentation](scripts/README.md)
- [Tests Documentation](tests/README.md)
