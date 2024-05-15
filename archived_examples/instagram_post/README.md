# AI Crew for Instagram Post
## Introduction
This project is an example using the CrewAI framework to automate the process of coming up with an instagram post. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

#### Instagram Post
[![Instagram Post](https://img.youtube.com/vi/lcD0nT8IVTg/0.jpg)](https://www.youtube.com/watch?v=lcD0nT8IVTg "Instagram Post")

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Using Local Models with Ollama](#using-local-models-with-ollama)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to give a complete stock analysis and investment recommendation

## Running the Script
This example uses OpenHermes 2.5 through Ollama by default so you should to download [Ollama](ollama.ai) and [OpenHermes](https://ollama.ai/library/openhermes).

You can change the model by changing the `MODEL` env var in the `.env` file.

- **Configure Environment**: Copy ``.env.example` and set up the environment variables for [Browseless](https://www.browserless.io/), [Serper](https://serper.dev/).
- **Install Dependencies**: Run `poetry install --no-root`.
- **Execute the Script**: Run `python main.py` and input your idea.

## Details & Explanation
- **Running the Script**: Execute `python main.py`` and input your idea when prompted. The script will leverage the CrewAI framework to process the idea and generate a landing page.
- **Key Components**:
  - `./main.py`: Main script file.
  - `./tasks.py`: Main file with the tasks prompts.
  - `./agents.py`: Main file with the agents creation.
  - `./tools/`: Contains tool classes used by the agents.

## Using Local Models with Ollama
This example run enterily local models, the CrewAI framework supports integration with both closed and local models, by using tools such as Ollama, for enhanced flexibility and customization. This allows you to utilize your own models, which can be particularly useful for specialized tasks or data privacy concerns.

### Setting Up Ollama
- **Install Ollama**: Ensure that Ollama is properly installed in your environment. Follow the installation guide provided by Ollama for detailed instructions.
- **Configure Ollama**: Set up Ollama to work with your local model. You will probably need to [tweak the model using a Modelfile](https://github.com/jmorganca/ollama/blob/main/docs/modelfile.md), I'd recommend playing with `top_p` and `temperature`.

## License
This project is released under the MIT License.
