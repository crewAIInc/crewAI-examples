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

- Python 3.9+
- AWS Account with Bedrock access
- AWS credentials configured
- Access to Claude-3 Sonnet model in Bedrock

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
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
MAX_OUTPUT_TOKENS=4096
TEMPERATURE=0.7
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```
### Usage

Analyze a research paper using either method:
Direct Python execution:

    poetry run python main.py path/to/your/paper.pdf

Using CrewAI CLI:
    
    poetry run crew run --pdf_path path/to/your/paper.pdf

### Project Structure

research-paper-analyzer/
├── main.py                 # Main execution script
├── analyze_paper.py        # CrewAI process file
├── crew.yaml              # CrewAI configuration
├── pyproject.toml        # Poetry configuration
├── README.md
├── agents.py             # Agent definitions
├── tasks.py             # Task definitions
└── utils/
    ├── __init__.py
    ├── Bedrock.py       # AWS Bedrock integration
    └── PdfReader.py     # PDF processing utilities

Features

    Comprehensive Analysis: Multi-faceted examination of research papers
    AWS Bedrock Integration: Leverages powerful Claude-3 model
    Modular Architecture: Separate specialized agents for different aspects
    PDF Processing: Automatic extraction and processing of PDF papers
    Structured Output: Clear, organized analysis reports

### Running Tests

    poetry run pytest

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

    CrewAI 
