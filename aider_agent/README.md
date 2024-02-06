# Using aider with crewAI

## Introduction
This is a simple example using the CrewAI framework with the Aider coding assistant tool.

## Running the Script
This example reads a code file, such as `bad.py`, uses local models to make a recommended list of changes to the code. The list of changes is then passed to aider to apply the modifications to the code using OpenAI models. 

- **Configure Environment**: Copy ``.env.example` and set up the environment variables the model, endpoint url, and api key.
- **Install Dependencies**: Run `poetry install --no-root`.
- **Execute the Script**: Run `python main.py` to see a list of recommended changes to this document.

## Details & Explanation
- **Running the Script**: Execute `python main.py bad.py`. The script will leverage the CrewAI framework to read the file, pass it to local models, and allow the agent apply changes to the file using aider.

## License
This project is released under the MIT License.