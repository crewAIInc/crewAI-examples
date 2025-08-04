# CrewAI Standard Crews Examples

This directory contains examples of traditional CrewAI implementations - autonomous agent teams working together to accomplish complex tasks.

## What are CrewAI Crews?

A CrewAI Crew is a team of AI agents, each with specific roles and goals, working together to complete tasks. Key components include:
- **Agents**: Autonomous AI entities with specific roles and expertise
- **Tasks**: Defined objectives that agents work to complete
- **Tools**: Functions and integrations agents can use
- **Process**: Sequential or hierarchical task execution

## Examples in this Directory

### Content Creation
- **game-builder-crew**: Multi-agent team that designs and builds Python games
- **instagram_post**: Creates engaging Instagram content with research and creativity
- **landing_page_generator**: Builds complete landing pages from concepts
- **marketing_strategy**: Develops comprehensive marketing campaigns
- **screenplay_writer**: Converts text into professional screenplay format

### Business & Productivity
- **job-posting**: Analyzes companies and creates tailored job descriptions
- **prep-for-a-meeting**: Researches participants and prepares meeting strategies
- **recruitment**: Automates candidate sourcing and evaluation
- **stock_analysis**: Performs comprehensive financial analysis with SEC data

### Data & Matching
- **match_profile_to_positions**: CV-to-job matching with vector search
- **meta_quest_knowledge**: Q&A system using PDF documentation

### Travel & Planning
- **surprise_trip**: Plans personalized surprise travel itineraries
- **trip_planner**: Compares destinations and optimizes travel plans

### Template
- **starter_template**: Basic template for creating new CrewAI projects

## Common Crew Patterns

### Agent Definition
```yaml
# agents.yaml
researcher:
  role: "Senior Research Analyst"
  goal: "Uncover cutting-edge developments"
  backstory: "You're a seasoned researcher..."
```

### Task Definition
```yaml
# tasks.yaml
research_task:
  description: "Conduct comprehensive research on {topic}"
  agent: researcher
  expected_output: "Detailed research report"
```

### Crew Assembly
```python
from crewai import Crew, Agent, Task

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process="sequential"  # or "hierarchical"
)
```

## Key Features Demonstrated

1. **Multi-Agent Collaboration**: Examples show 2-7 agents working together
2. **Tool Integration**: Web search, APIs, file manipulation, databases
3. **Custom Tools**: Many examples implement specialized tools
4. **YAML Configuration**: Standardized agent/task definitions
5. **Various Domains**: From creative writing to financial analysis

## Getting Started

1. Choose an example that matches your use case
2. Navigate to its directory
3. Follow the example-specific README
4. Install dependencies (usually via `pip install -r requirements.txt` or `poetry install`)
5. Run with `python main.py` or as specified

Each example is self-contained with all necessary configurations and can be used as a starting point for your own crews.