# AI Crew using NVIDIA NIM Endpoint

## Introduction
This is a simple example using the CrewAI framework with an NVIDIA endpoint and langchain-nvidia-ai-endpoints integration.

## Running the Script
This example show cases the NVIDIA NIM endpoint integration with CrewAI.

- **Configure Environment**: Set NVIDIA_API_KEY to appropriate api key.
                             Set MODEL to select appropriate model
                             Set NVIDIA_API_URL to select the endpoint(Catalogue/local endpoint)
- **Install Dependencies**: Run `make install`.
- **Execute the Script**: Run `python main.py` to see a list of recommended changes to this document.

## Details & Explanation
- **Running the Script**: Execute `python main.py`. The script will leverage the CrewAI framework to process the specified file and return a list of changes.