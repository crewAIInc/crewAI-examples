# Gestell Crew Orchestration Guide

In this guide, you’ll learn how to use the Gestell MCP Server to create Crew Agents that:

1. Create and configure a new collection
2. Upload documents into your collection
3. Navigate table categories in the Gestell Console
4. Use an AI agent to research your collection and generate summaries

View a video walkthrough of this end-to-end orchestration on [Gestell’s YouTube channel](https://youtu.be/V73zXKUuQHc).

## Why use Gestell?

Gestell is an ETL for AI search and reasoning. Connect any unstructured data source and Gestell will enable at-scale, efficient and accurate search and reasoning for your application. No need for complex and costly processing and RAG pipelines – simply instruct Gestell in natural language and get production-scale databases setup instantly.

### Advantages

- Ease: Add Gestell to your CrewAI implementation in just a few lines of code to get your unstructured datasets integrated to your Crew
- Scale: Process massive unstructured databases with best-in-class performance
- Simplicity: No need for complex RAG or agentic search architectures - simply instruct in natural language how you want your data structured
- Customization: Create specific categories tailored to your business workflows using natural language instructions. Extract features, overlay concepts, and build specialized knowledge bases

### How Gestell Works with CrewAI

CrewAI excels at orchestrating AI agents to tackle complex tasks, while Gestell transforms raw data into AI-ready, structured information. Together, they create a powerful system where:

1. Context Delivery: Gestell's search and reasoning platform provides CrewAI agents with richer, more accurate context for decision-making
2. Specialized Knowledge Bases: Create domain-specific knowledge structures that CrewAI agents can efficiently query and reason with
3. Scalable Reasoning: As your data grows, Gestell's ETL pipeline ensures your CrewAI implementation maintains high performance without degradation
4. Seamless Integration: The integration process is straightforward, allowing you to focus on building your AI application rather than wrestling with data preparation
5. End-to-End Solution: From data ingestion to agent execution, get a complete workflow that handles the complexity of unstructured data and multi-agent coordination

## Running The Examples

- You need `node` installed and `uv` installed

- You also need a Gestell API Key which you can get from the [Gestell Platform](https://platform.gestell.ai)

- Copy the `.env.sample` file to `.env` and fill in the values

### Usage

```bash
# Edit src/download.py to download the wikipedia files you want to download
uv run src/download.py
# NOTE: If you don't want wikipedia articles
# You can also put video, audio, or any other file in `files/`. Gestell will process it for you.

# After you have items in `files/`, start the document analysis and collection creation Crew
uv run src/create.py

# Review the status of documents being processed on https://platform.gestell.ai
# Once all documents are processed, run the research Crew
uv run src/research.py

# You will be given a research report in `agent/research_report.md`
cat agent/research_report.md
```
