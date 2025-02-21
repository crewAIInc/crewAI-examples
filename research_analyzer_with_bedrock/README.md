# Research Paper Analyzer with Bedrock

A sophisticated research paper analysis system powered by [CrewAI](https://crewai.com) and [Amazon Bedrock](https://aws.amazon.com/bedrock/). This project leverages multiple specialized AI agents to perform comprehensive analysis of academic papers, providing detailed technical analysis, literature review, and actionable insights.

## Overview

The Research Paper Analyzer uses a team of specialized AI agents to analyze academic papers through several phases:

1. **Technical Analysis**: Detailed examination of methodology, statistical approaches, and results
2. **Literature Review**: Contextualization within the broader academic landscape
3. **Summary Creation**: Synthesis of key findings and contributions
4. **Final Report Generation**: Comprehensive report with insights and recommendations

### High-Level Architecture

The system operates through four specialized agents:

- **Research Director**: Coordinates analysis and ensures quality
- **Technical Expert**: Analyzes methodologies and statistical significance
- **Literature Specialist**: Reviews research context and connections
- **Summary Writer**: Creates clear, accessible summaries

## Installation

### Prerequisites

- Python 3.10+
- AWS Account with Amazon Bedrock access
- An AWS IAM role with permissions to access Amazon Bedrock, configured following [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#bp-workloads-use-roles)
- [Access to Claude-3.5 Sonnet model](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html) in Amazon Bedrock

### Setup

1. Clone the repository:
```bash
git clone https://github.com/crewAIInc/crewAI-examples.git
cd research_analyzer_with_bedrock
```
2. Install dependencies using Poetry:
```bash
poetry install --no-root
```
3. Create a .env file in the project root:
```bash
AWS_REGION_NAME=us-west-2
BEDROCK_MODEL_ID=bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0
MAX_OUTPUT_TOKENS=4096
TEMPERATURE=0.7
```
### Usage

Analyze a research paper using either method:
Direct Python execution:

    poetry run python main.py path/to/your/paper.pdf

Using CrewAI CLI:
    
    poetry run crew run --pdf_path path/to/your/paper.pdf

Features

    Comprehensive Analysis: Multi-faceted examination of research papers
    AWS Bedrock Integration: Leverages powerful Claude-3 model
    Modular Architecture: Separate specialized agents for different aspects
    PDF Processing: Automatic extraction and processing of PDF papers
    Structured Output: Clear, organized analysis reports

## License

This project is licensed under the MIT License - see the LICENSE file for details.
