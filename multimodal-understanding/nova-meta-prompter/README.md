# Amazon Nova Meta Prompter

Transform prompts to align with Amazon Nova guidelines.

## Quick Start

### Interactive Notebook (Recommended)

Open `nova_metaprompter_showcase.ipynb` to transform prompts:

```bash
# Set your AWS credentials
export AWS_PROFILE=your-profile-name
export AWS_REGION=us-west-2

# Launch Jupyter
jupyter notebook nova_metaprompter_showcase.ipynb
```

The notebook provides:
- **Prompt Transformation**: Align prompts with Nova guidelines
- **Analysis & Reflection**: Detailed transformation process with reasoning
- **Multiple Models**: Support for Nova Premier and Claude Sonnet 4.5

### Python API

Use the transform function directly in your code:

```python
from transform import transform_prompt

# Transform using default Nova Premier model
current_prompt = "Summarize this document: {document_text}"
result = transform_prompt(current_prompt)

print("Nova-aligned prompt:")
print(result['nova_final'])

# Or use Claude Sonnet 4.5
result = transform_prompt(
    current_prompt,
    model_id='global.anthropic.claude-sonnet-4-5-20250929-v1:0'
)
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd nova_metaprompter

# Install dependencies
pip install -e .
```

## Configuration

### AWS Credentials

Configure via environment variables (recommended):

```bash
export AWS_PROFILE=your-profile-name
export AWS_REGION=us-west-2
```

Or use AWS CLI:

```bash
aws configure
```

**Note**: The SDK automatically detects region from your AWS configuration. No hard-coded regions required.

## Available Models

- **`us.amazon.nova-premier-v1:0`** (default) - Amazon Nova Premier
- **`global.anthropic.claude-sonnet-4-5-20250929-v1:0`** - Claude Sonnet 4.5

## Project Structure

```
nova_metaprompter/
├── transform.py                          # Main transformation function
├── nova_metaprompter_showcase.ipynb      # Interactive notebook
├── data/                                 # Prompt templates and docs
│   ├── prompts/
│   └── docs/
├── pyproject.toml
└── README.md
```

## What It Does

- Analyzes your existing prompts
- Identifies alignment opportunities with Nova guidelines
- Adapts prompts for Nova models' capabilities
- Provides detailed reasoning and reflection

## Nova Guidelines Applied

- **Clear section headers** using ## format
- **Specific task descriptions** and context
- **Step-by-step instructions** when beneficial
- **Structured output requirements**
- **Optimized formatting** for Nova models' reasoning capabilities

## Amazon Nova Premier Advantages

- **Extended Context**: 1M token context window
- **Cost Effective**: Lower cost per token
- **Structured Output**: Native JSON/XML formatting support
- **Multimodal**: Built-in image/video understanding
- **AWS Native**: Seamless integration with AWS services

## Requirements

- Python 3.12+
- AWS Bedrock access with Nova model permissions
- Valid AWS credentials configured

---

**Get started with the notebook for an interactive experience transforming your prompts.**
