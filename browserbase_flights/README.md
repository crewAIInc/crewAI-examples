# crewAI + Browserbase flight search

The following is a multi-task, multi-agent, multi-tool example for AI-based flight search using Skyscanner and Browserbase.

## Installation

```
pip install crewai 'crewai[tools]' html2text playwright
```

Set the required environment variables:

```
export OPENAI_API_KEY=
export BROWSERBASE_API_KEY=
```

Optionally, set a different model in CrewAI:

```
export OPENAI_MODEL_NAME=gpt-4-turbo
```

## Demo

```
python3 demo.py "Sofia to Berlin one-way on 26th May"
```
