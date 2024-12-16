
# AI Crew for Marketing Strategy using NVIDIA NIM Endpoint
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of a marketing strategy. CrewAI orchestrates autonomous AI agents powered by NVIDIA LLM endpoints, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [NVIDIA NIM](https://docs.api.nvidia.com/?ncid=no-ncid)
- [langchain-nvidia-ai-endpoints](https://github.com/langchain-ai/langchain-nvidia)

# NVIDIA NIMs

The `langchain-nvidia-ai-endpoints` package contains LangChain integrations building applications with models on
NVIDIA NIM inference microservice. NIM supports models across domains like chat, embedding, and re-ranking models
from the community as well as NVIDIA. These models are optimized by NVIDIA to deliver the best performance on NVIDIA
accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single
command on NVIDIA accelerated infrastructure.

NVIDIA hosted deployments of NIMs are available to test on the [NVIDIA API catalog](https://build.nvidia.com/). After testing,
NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud,
giving enterprises ownership and full control of their IP and AI application.

NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog.
At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.

This example goes over how to use LangChain to interact with NVIDIA supported via the `ChatNVIDIA` class.

For more information on accessing the chat models through this api, check out the [ChatNVIDIA](https://python.langchain.com/docs/integrations/chat/nvidia_ai_endpoints/) documentation.

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to create a comprehensive marketing strategy and develop compelling marketing content.

## Running the Script
It uses meta/llama-3.1-8b-instruct by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [NVIDIA](https://build.nvidia.com) and other tools as needed, like [Serper](serper.dev).
- **Install Dependencies**: Run `make install`.
- **Customize**: Modify `src/marketing_posts/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/marketing_posts/config/agents.yaml` to update your agents and `src/marketing_posts/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run marketing_posts` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run marketing_posts`. The script will leverage the CrewAI framework to generate a detailed marketing strategy.
- **Key Components**:
  - `src/marketing_posts/main.py`: Main script file.
  - `src/marketing_posts/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/marketing_posts/config/agents.yaml`: Configuration file for defining agents.
  - `src/marketing_posts/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/marketing_posts/tools`: Contains tool classes used by the agents.
