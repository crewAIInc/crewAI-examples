# AI Crew for Reviewing Markdown Syntax

## Introduction
This project is an example using the CrewAI framework to automate the process reviewing a markdown file for syntax issues. A general assistant leverages a custom tool to get a list of markdown linting errors. It then summarizes those errors into a list of changes to make to the document.

## Running the Script
This example uses the OpenAI API to call a model. This can be through a locally hosted solution like LM Studio, or the Open AI API endpoint with your API key. 

=======
- **Configure Environment**: Rename `.env.example` to `.env` and set up the environment variables the model, endpoint url, and api key.
- **Install Dependencies**: Run `poetry install --no-root`.
- **Install Dependencies**: Run `poetry lock`.
- **Execute the Script**: Run `python main.py README.md` to see a list of recommended changes to this document.

## Details & Explanation
- **Running the Script**: Execute `poetry run markdown_validator {filename}`. The script will leverage the CrewAI framework to process the specified file and return a list of changes.
- **Running the Script with agent training**: Execute `poetry run train {number_of_iterations} {filename}`. The script will leverage the CrewAI framework to process the specified file and return a list of changes, and updates the changes according to the user's feedback.

## License
This project is released under the MIT License.
