# TripPlanner with CrewAI

Welcome to TripPlanner with CrewAI, a sophisticated travel planning system powered by [crewAI](https://crewai.com). This project leverages a multi-agent AI system to create comprehensive travel plans tailored to your preferences.

## Overview

TripPlanner with CrewAI utilizes a team of specialized AI agents to research destinations, find optimal travel options, search for accommodations, plan detailed itineraries, and compile comprehensive travel reports. The system is designed to provide a seamless and personalized travel planning experience.

## Key Features

- Destination research and analysis
- Travel options optimization (flights or car travel)
- Accommodation recommendations
- Detailed daily itinerary planning
- Comprehensive travel report generation

## Installation

Ensure you have Python >=3.10 <3.13 installed. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

1. Install UV:

   ```bash
   pip install uv
   ```

2. Install dependencies:

   ```bash
   crewai install
   ```

3. Add your env variables to the `.env` file.

* `OPENAI_API_KEY` - API key for the [OpenAI API](https://platform.openai.com/docs/guides)
* `SERPAPI_API_KEY` - API key for the [Serp API](https://serpapi.com/dashboard)
* `SERPER_API_KEY` - API key for the [Serper](https://serper.dev/)

## Configuration

- `src/trip_planner/config/agents.yaml`: Define AI agents (e.g., destination researcher, travel options specialist)
- `src/trip_planner/config/tasks.yaml`: Specify tasks for each agent
- `src/trip_planner/crew.py`: Customize logic, tools, and arguments
- `src/trip_planner/main.py`: Add custom inputs for agents and tasks

## Usage

Run the TripPlanner with CrewAI from the project root:

```bash
crewai run
```

This command initializes the AI agents and executes the travel planning process based on your configurations.

## AI Agents

- Destination Research Specialist
- Travel Options Specialist
- Accommodation Specialist
- Itinerary Planner
- Travel Report Compiler

Each agent has specific roles and goals, collaborating to create a comprehensive travel plan.

## Output

The system generates a detailed travel report (`report.md`) in the root folder, including:

1. Executive Summary
2. Destination Overview
3. Travel Options
4. Accommodation Recommendations
5. Detailed Daily Itinerary
6. Dining and Culinary Experiences
7. Additional Information
8. Conclusion

## Support

For assistance or inquiries:

- [Documentation](https://docs.crewai.com)
- [GitHub Repository](https://github.com/joaomdmoura/crewai)
- [Discord Community](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Experience the future of travel planning with TripPlanner AI!
