# CrewAI Flows Examples

This directory contains examples demonstrating the CrewAI Flows pattern - a powerful orchestration framework for managing complex, multi-crew workflows with state management.

## What are CrewAI Flows?

CrewAI Flows allow you to:
- Orchestrate multiple crews in sequence or parallel
- Manage state across different execution steps
- Implement conditional logic and routing
- Create human-in-the-loop workflows
- Build complex automation pipelines

## Examples in this Directory

### 1. Content Creator Flow
Multi-crew content generation system that:
- Routes requests to specialized crews (Blog, LinkedIn, Research)
- Generates professional content across different formats
- Uses advanced orchestration with dynamic routing
- Demonstrates complex multi-agent workflows

### 2. Email Auto Responder Flow
Automated email monitoring and response generation system that:
- Monitors Gmail inbox at regular intervals
- Filters and categorizes incoming emails
- Generates appropriate draft responses
- Maintains state of processed emails

### 3. Lead Score Flow
Lead qualification and outreach automation that:
- Processes leads from CSV files
- Scores and ranks leads based on criteria
- Implements human review for top candidates
- Generates personalized outreach emails

### 4. Meeting Assistant Flow
Meeting productivity automation that:
- Processes meeting transcripts and notes
- Extracts action items and decisions
- Creates tasks in Trello
- Sends notifications via Slack

### 5. Self Evaluation Loop Flow
Iterative content improvement system that:
- Generates content (e.g., social media posts)
- Self-evaluates against criteria
- Automatically refines based on feedback
- Implements retry logic with limits

### 6. Write a Book with Flows
Book creation automation that:
- Generates book outlines
- Writes chapters in parallel
- Maintains consistency across sections
- Compiles final manuscript

## Common Flow Patterns

### Sequential Execution
```python
# Execute crews one after another
flow = Flow()
flow.add_crew(crew1)
flow.add_crew(crew2)
```

### Parallel Execution
```python
# Execute multiple crews simultaneously
await flow.run_parallel([crew1, crew2, crew3])
```

### Conditional Routing
```python
# Route based on previous results
@flow.router
def route_based_on_result(state):
    if state.score > 0.8:
        return "high_quality_path"
    return "needs_improvement_path"
```

### Human-in-the-Loop
```python
# Pause for human input
human_feedback = flow.wait_for_input("Review these results")
```

## Getting Started

Each example includes:
- Complete working code
- Configuration files
- README with specific instructions
- Required dependencies

Choose an example that matches your use case and follow its README for setup instructions.