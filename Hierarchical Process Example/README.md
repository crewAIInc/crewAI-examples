# Introduction
This repository provides a simple example demonstrating the implementation of the Hierarchical Process within the CrewAI framework using the Google Gemini API.

## Config Setup
To execute this example, the Gemini API is utilized for model calls. Ensure you have the necessary API key in place (SERPER API key and Browserless API).

## Running the Notebook
Before running the notebook, confirm that the country in `!curl ipinfo.io` is among the countries with access to the Google Gemini API. Refer to the available regions [here](https://ai.google.dev/available_regions#available_regions).
If your country is not in the access list try to restart your runtime and try again, The runtime location is independent of your location.

Follow these steps:

Install the required packages by running the following command twice:
```
%pip install -U --quiet langchain-google-genai pillow langchain google-search-results crewai unstructured langgraph langchainhub
```
Note: The first attempt might fail, but it should succeed on the second attempt.

Execute all the cells in the notebook. Optionally, you can create Agents and Tasks to explore and experiment further. Feel free to try different scenarios!
