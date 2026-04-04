# CrewAI Full Examples

## Overview
A comprehensive collection of production-ready applications built with the CrewAI framework for orchestrating autonomous AI agents.

## Project Structure
```
.
├── app.py                  # Flask dashboard (landing page)
├── crews/                  # Standard CrewAI crew implementations
├── flows/                  # Advanced CrewAI flow orchestrations
├── integrations/           # Third-party integrations (LangGraph, Azure, NVIDIA)
├── notebooks/              # Jupyter notebooks for learning
└── README.md               # Full project documentation
```

## Tech Stack
- **Language**: Python 3.12
- **Package Manager**: uv (per-example) + pip (global)
- **Web Framework**: Flask (dashboard only)
- **AI Framework**: CrewAI v0.152.0
- **Production Server**: Gunicorn

## Running the App
The dashboard runs on port 5000 via Flask (`app.py`).
- Development: `python app.py`
- Production: `gunicorn --bind=0.0.0.0:5000 --reuse-port app:app`

## Individual Examples
Each example under `crews/`, `flows/`, and `integrations/` is a standalone Python package with its own `pyproject.toml` and dependencies managed via `uv`.

To run an individual example:
```bash
cd crews/marketing_strategy
uv sync
uv run python main.py
```

Most examples require an `OPENAI_API_KEY` environment variable.

## Deployment
Configured for autoscale deployment using Gunicorn on port 5000.
