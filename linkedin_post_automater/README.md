# 💼 LinkedinPostAutomater Crew

Welcome to **LinkedIn Post Automater** — an intelligent, multi-agent system powered by [crewAI](https://crewai.com) that transforms how professionals create and publish content on LinkedIn.

Whether you're building your personal brand or managing corporate communication, this system automates the heavy lifting: from sourcing trending news to crafting and posting impactful updates — all done intelligently and consistently.

---

## 🚀 What It Does

🔹 **Real-time News Discovery**  
Finds and summarizes the latest developments around a selected topic.

🔹 **Content Planning & Research**  
Structures content with a clear outline, key points, and supporting facts.

🔹 **Post Writing & Publishing**  
Generates professional, LinkedIn-optimized content and automatically publishes it.

🔹 **Visual Enhancement**  
Creates an engaging visual using AI to enhance post visibility and appeal.

---

## 🌟 Why Use LinkedIn Post Automater?

- 🧠 Stay Relevant: Tap into current news without endless research.
- ✍️ Post Smarter: Get structured, well-written content every time.
- 🖼️ Stand Out: Add AI-generated visuals to attract attention in feeds.
- ⏳ Save Time: Automate the whole process — from ideation to publishing.

---

## 🤖 Behind the Scenes

This project uses a **multi-agent architecture**, where each AI agent has a specific role:

| Agent                          | Purpose                                 |
|-------------------------------|-----------------------------------------|
| News_Article_Researcher       | Gathers trending news and insights      |
| Planner_and_Researcher        | Crafts a content plan with structure     |
| Article_Maker_and_LinkedIn_Poster | Writes and posts the article on LinkedIn |

Agents collaborate using crewAI’s intelligent workflow orchestration — ensuring efficient execution, quality output, and full automation.

---
## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `Linkedin_access_token` , `GEMINI_API_KEY` , `RAPIDAPI_KEY` , `MODEL` into the `.env` file**

- Modify `src/linkedin_post_automater/config/agents.yaml` to define your agents
- Modify `src/linkedin_post_automater/config/tasks.yaml` to define your tasks
- Modify `src/linkedin_post_automater/crew.py` to add your own logic, tools and specific args
- Modify `src/linkedin_post_automater/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the linkedin_post_automater Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The linkedin_post_automater Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.


## 👥 Who Is This For?

- 🔹 Founders & Entrepreneurs  
- 🔹 Personal Brand Builders  
- 🔹 B2B Marketers  
- 🔹 Content Teams  
- 🔹 AI & Automation Enthusiasts

---

## 📌 Project Outcomes

When you run the system:
- A professional article is saved as `report.md`
- Supporting news is listed in `news.md`
- A post image is created with Gemini AI
- The final post is shared on your LinkedIn account

All of this — with **zero manual effort**.

---

## 💬 Need Help?

We're here to support your journey:

- Explore the [crewAI documentation](https://docs.crewai.com)  
- Contribute on [GitHub](https://github.com/joaomdmoura/crewai)  
- Connect on [Discord](https://discord.com/invite/X4JWnZnxPb)  
- [Chat with the docs](https://chatg.pt/DWjSBZn)

---

> “Let your AI team manage your LinkedIn while you focus on leading.”  
— *LinkedinPostAutomater Crew*

