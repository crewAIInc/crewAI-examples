# CrewAI Full Examples

## Introduction
Welcome to the official collection of **complete CrewAI applications**. This repository contains end-to-end implementations that showcase how to build real-world applications using CrewAI's framework for orchestrating AI agents.

> **🍳 Looking for feature-specific tutorials?** Check out [CrewAI Cookbook](https://github.com/crewAIInc/crewAI-cookbook) for focused guides on specific CrewAI features and patterns.

## What You'll Find Here

These are **full applications** that demonstrate:
- Complete project structures and organization
- Real-world integration patterns (APIs, databases, external services)
- Comprehensive code implementations with error handling
- End-to-end workflows from input to output
- Industry-specific implementations across various domains

Each example is a standalone application you can run, modify, and deploy.

**Note**: All examples use **CrewAI version 0.152.0** and **UV package management** for optimal performance and developer experience.

## 📁 Repository Structure

### 🌊 [Flows](/flows)
Advanced orchestration examples using CrewAI Flows for complex workflows with state management.

- [Content Creator Flow](flows/content_creator_flow) - Multi-crew content generation system for blogs, LinkedIn posts, and research reports
- [Email Auto Responder Flow](flows/email_auto_responder_flow) - Automated email monitoring and response generation
- [Lead Score Flow](flows/lead-score-flow) - Lead qualification with human-in-the-loop review
- [Meeting Assistant Flow](flows/meeting_assistant_flow) - Meeting notes processing with Trello/Slack integration
- [Self Evaluation Loop Flow](flows/self_evaluation_loop_flow) - Iterative content improvement with self-review
- [Write a Book with Flows](flows/write_a_book_with_flows) - Automated book writing with parallel chapter generation

### 👥 [Crews](/crews)
Traditional CrewAI implementations showcasing multi-agent collaboration.

#### Content Creation & Marketing
- [Game Builder Crew](crews/game-builder-crew) - Multi-agent team that designs and builds Python games
- [Instagram Post](crews/instagram_post) - Creative social media content generation
- [Landing Page Generator](crews/landing_page_generator) - Full landing page creation from concepts
- [Marketing Strategy](crews/marketing_strategy) - Comprehensive marketing campaign development
- [Screenplay Writer](crews/screenplay_writer) - Convert text/emails into screenplay format

#### Business & Productivity
- [Job Posting](crews/job-posting) - Automated job description creation
- [Prep for a Meeting](crews/prep-for-a-meeting) - Meeting preparation research and strategy
- [Recruitment](crews/recruitment) - Automated candidate sourcing and evaluation
- [Stock Analysis](crews/stock_analysis) - Financial analysis with SEC data integration

#### Data & Research
- [Industry Agents](crews/industry-agents) - Industry-specific agent implementations
- [Match Profile to Positions](crews/match_profile_to_positions) - CV-to-job matching with vector search
- [Meta Quest Knowledge](crews/meta_quest_knowledge) - PDF-based Q&A system
- [Markdown Validator](crews/markdown_validator) - Automated markdown validation and correction

#### Travel & Planning
- [Surprise Trip](crews/surprise_trip) - Personalized surprise travel planning
- [Trip Planner](crews/trip_planner) - Destination comparison and itinerary optimization

#### Templates
- [Starter Template](crews/starter_template) - Basic template for new CrewAI projects

### 🔌 [Integrations](/integrations)
Examples showing CrewAI integration with other platforms and services.

- [CrewAI-LangGraph](integrations/CrewAI-LangGraph) - Integration with LangGraph framework
- [Azure Model](integrations/azure_model) - Using CrewAI with Azure OpenAI
- [NVIDIA Models](integrations/nvidia_models) - Integration with NVIDIA's AI ecosystem

### 📓 [Notebooks](/Notebooks)
Jupyter notebook examples for interactive exploration and learning.

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/crewAIInc/crewAI-examples.git
   cd crewAI-examples
   ```

2. **Choose an example category**
   - For multi-crew orchestration → check `/flows`
   - For standard crews → check `/crews`
   - For platform integrations → check `/integrations`

3. **Navigate to specific example**
   ```bash
   cd crews/marketing_strategy  # or any other example
   ```

4. **Install dependencies with UV**
   ```bash
   uv sync  # Installs all dependencies and creates virtual environment
   ```

5. **Follow the example's README**
   Each example contains specific setup instructions and usage guides

## 📚 Learning Path

### Beginners
Start with:
1. [Starter Template](crews/starter_template) - Basic crew structure
2. [Instagram Post](crews/instagram_post) - Simple content creation
3. [Job Posting](crews/job-posting) - Straightforward business use case

### Intermediate
Explore:
1. [Marketing Strategy](crews/marketing_strategy) - Multi-agent collaboration
2. [Self Evaluation Loop Flow](flows/self_evaluation_loop_flow) - Iterative workflows
3. [Stock Analysis](crews/stock_analysis) - External API integration

### Advanced
Deep dive into:
1. [Content Creator Flow](flows/content_creator_flow) - Multi-crew orchestration with dynamic routing
2. [Write a Book with Flows](flows/write_a_book_with_flows) - Complex parallel execution
3. [Lead Score Flow](flows/lead-score-flow) - Human-in-the-loop patterns
4. [CrewAI-LangGraph](integrations/CrewAI-LangGraph) - Framework integration

## 🛠 Common Patterns

- **Configuration**: Most examples use YAML files for agent/task definitions
- **Tools**: Examples showcase integration with APIs, databases, and file systems
- **Flows**: Advanced examples demonstrate state management and orchestration
- **Training**: Several examples include agent training capabilities

## 📝 Contributing

We welcome contributions! Please feel free to submit examples showcasing new use cases or improvements to existing ones.

## 📄 License

This repository is maintained by the CrewAI team. Check individual examples for specific licensing information.

---

## 🔗 Related Resources

- **[CrewAI Framework](https://github.com/crewAIInc/crewAI)** - Main CrewAI repository
- **[CrewAI Cookbooks](https://github.com/crewAIInc/crewAI-cookbook)** - Feature-focused tutorials and guides
- **[CrewAI Documentation](https://docs.crewai.com)** - Comprehensive documentation
- **[CrewAI Community](https://community.crewai.com)** - Join our community discussions