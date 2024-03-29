# Due Diligence Interview

By [@JosemyDuarte](https://github.com/JosemyDuarte)

## Description

Here you will find the implementation of a crew of AI agents that will investigate a company for you, helping you prepare for an interview. These agents will gather relevant information about the company and industry to provide you with valuable insights.

## Requirements

- Python 3.12 or higher
- pip
- [ollama](https://ollama.com/)
- +32GB of RAM (for the LLM model, can be reduced by using a smaller model)

## Installation

1. Clone the repository

2. Create a virtual environment
    ```bash
    python -m venv venv
    ```
   
3. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
   
4. Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```
   
5. Download local LLM model. I'm using [this one](https://ollama.com/library/mixtral:8x7b-instruct-v0.1-q6_K)
    ```bash
    ollama pull mixtral:8x7b-instruct-v0.1-q6_K
    ```
   
**Note**: You can also use a different LLM model for the agents. Just replace the model name used for the `llm` variable on the `main.py` file.

## Usage

1. Run the main script to start the investigation:

    ```bash
    python main.py
    ```

2. Write the name of the company you are investigating

3. Review the generated reports and insights on the console.

Example report for **Twitter**

<img width="1783" alt="image" src="https://github.com/JosemyDuarte/DueDiligenceAI/assets/6247860/3037d8f8-50f4-43c7-8876-394c35e5254f">
