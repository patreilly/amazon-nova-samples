# Deployment Scripts

This directory contains scripts for deploying and managing the QA testing demo infrastructure on AWS.

## Scripts Overview

### 1. `deployment.sh` - Complete Deployment ✅
**Purpose**: Deploy the complete infrastructure and upload all application files.

**Usage**:
```bash
./deployment.sh
```

**What it does**:
- Creates CloudFormation stack with S3 bucket and CloudFront distribution
- Uploads all web application files to S3
- Configures security settings and permissions
- Creates CloudFront invalidation for immediate availability
- Provides the final application URL

**Use when**: First-time deployment or complete recreation needed
**Time**: ~10-15 minutes

### 2. `update-stack.sh` - Safe Updates
**Purpose**: Update existing CloudFormation stack with new template changes.

**Usage**:
```bash
./update-stack.sh
```

**What it does**:
- Creates a change set to preview modifications
- Shows exactly what will be changed before execution
- Applies updates to CloudFormation template
- Handles parameter validation intelligently

**Use when**: Updating CloudFormation template or configuration
**Time**: ~5-10 minutes

### 3. `invalidate-cloudfront.sh` - Cache Management
**Purpose**: Invalidate CloudFront cache to ensure updated content is visible immediately.

**Usage**:
```bash
./invalidate-cloudfront.sh
```

**What it does**:
- Automatically finds your CloudFormation stack
- Extracts the CloudFront Distribution ID from stack outputs
- Creates a cache invalidation for all files (`/*`)
- Provides tracking information and console links

**Use when**: Files changed but infrastructure unchanged
**Time**: ~1-2 minutes (effect takes 10-15 minutes)

## Quick Start

### First-Time Deployment
```bash
cd qa-testing-acbt-nova-act/scripts
./deployment.sh
```

### Update Existing Stack
```bash
cd qa-testing-acbt-nova-act/scripts
./update-stack.sh
```

### Refresh Cache Only
```bash
cd qa-testing-acbt-nova-act/scripts
./invalidate-cloudfront.sh
```

## Script Details

### deployment.sh Output Example
```
Creating CloudFormation stack...
✅ Stack creation initiated: qa-testing-demo-stack-20241024

Uploading application files...
✅ Files uploaded successfully

Creating CloudFront invalidation...
✅ Cache invalidated

🎉 Deployment Complete!
Website URL: https://d1234567890abc.cloudfront.net
S3 Bucket: qa-testing-demo-bucket-20241024
CloudFront Distribution: E39035B19DGDMB
```

### update-stack.sh Output Example
```
Creating change set for stack update...
✅ Change set created: update-20241024-150312

Preview of changes:
- S3 bucket encryption: ADDED
- CloudFront security headers: MODIFIED

Apply these changes? (y/n): y
✅ Stack updated successfully
```

### invalidate-cloudfront.sh Output Example
```
Found CloudFront Distribution ID: E39035B19DGDMB
✅ Invalidation created successfully!

Invalidation Details:
- ID: I2B2IA2I0ZYHZP9B5OF6UFYKC
- Status: InProgress
- Distribution: E39035B19DGDMB
- Paths: /*
```

## Prerequisites

- **AWS CLI configured** with appropriate permissions
- **jq installed** for JSON parsing
- **Bash shell** (macOS/Linux/WSL)
- **IAM permissions** for CloudFormation, S3, and CloudFront

### Installing jq
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Windows (WSL)
sudo apt-get install jq
```

## Troubleshooting

### Common Issues

1. **Script Permission Denied**
   ```bash
   chmod +x *.sh
   ```

2. **AWS CLI Not Configured**
   ```bash
   aws configure
   # Enter your AWS credentials and region
   ```

3. **"No CloudFront distribution found"**
   - Verify the CloudFormation stack exists and is complete
   - Check that `CreateCloudFront` parameter is set to `true`

4. **Stack Already Exists Error**
   - Use `update-stack.sh` instead of `deployment.sh`
   - Or delete the existing stack first if complete recreation is needed

5. **Template Validation Errors**
   - Ensure `cloudformation-template.yaml` exists in the parent directory
   - Check YAML syntax is valid

### Checking Stack Status
```bash
# List all stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Get specific stack details
aws cloudformation describe-stacks --stack-name qa-testing-demo-stack-YYYYMMDD
```

### Checking CloudFront Status
```bash
# List distributions
aws cloudfront list-distributions

# Check invalidation status
aws cloudfront get-invalidation --distribution-id YOUR_DISTRIBUTION_ID --id YOUR_INVALIDATION_ID
```

## Cost Considerations

- **CloudFormation**: No additional charges for stack operations
- **S3 Storage**: ~$0.01/month for static files
- **CloudFront**: Free tier includes 1TB data transfer
- **CloudFront Invalidations**: First 1,000 paths per month are free, then $0.005 per path

## File Structure

```
scripts/
├── README.md              # This file
├── deployment.sh          # Complete deployment script
├── update-stack.sh        # Stack update script
└── invalidate-cloudfront.sh # Cache invalidation script
```

## Security Notes

- Scripts use CloudFormation template: `../cloudformation-template.yaml`
- All resources are created with security best practices
- S3 buckets include encryption and secure transport policies
- CloudFront distributions include security headers
