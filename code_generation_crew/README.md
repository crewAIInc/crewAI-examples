# AI Crew - Code Generation Crew
## Introduction
This project is an example using the CrewAI framework to run agents that generate code, run it, and report the results. The Agent with `enable_code_execution=True` will be responsible for creating the code based on the tasks goal. The code will be executed and then the output will be passed to the reporting analyst.


#### Jobs postings

- [CrewAI Framework](#crewai-framework)
- [Requirements](#requirements)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [License](#license)


## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to give a complete stock analysis and investment recommendation.

## Requirements

Docker is required to run the script. If you don't have Docker installed, you can download it [here](https://www.docker.com/products/docker-desktop).

## Running the Script
- **Configure Environment**: Copy ``.env.example` and set up the environment variables for OpenAI.
- **Install Dependencies**: Run `pip install -r requirements.txt`.
- **Execute the Script**: Run `python main.py` and input your idea on the tasks.

## Details & Explanation
- **Running the Script**: Execute `python main.py`` and the crew will kickoff bringing the last 30 days of stocks from APPL and NVDA but the use-case here is to show-up the Code Intepreter ability of the Anget.

The logic will take advantage of the structure that CrewAI provides, so that the agent can create the code and execute it.
After executing the code created by the agent himself, if for some reason it was not correct, the output was passed on to the same agent so that he can correct the code and run it again, after being executed correctly and the output will be passed on to the report analyst.


- **Key Components**:
  - `./main.py`: Main script file.
  - `./tasks.py`: Main file with the tasks prompts.
  - `./agents.py`: Main file with the agents creation.


## Example

In the example below, the agent created the code to fetch the last 30 days of stock prices for APPL and NVDA, run it, and printed the results so it can be sent to the reporting analyst.

```bash
Action: Code Interpreter
Action Input: {"code": "import yfinance as yf\nimport pandas as pd\nfrom datetime import datetime, timedelta\n\n# Define the time range\nend_date = datetime.now()\nstart_date = end_date - timedelta(days=30)\n\n# Fetch stock data\nappl_data = yf.download('AAPL', start=start_date, end=end_date)\nnvda_data = yf.download('NVDA', start=start_date, end=end_date)\n\n# Get the last 30 days of stock prices\nappl_prices = appl_data['Close']\nnvda_prices = nvda_data['Close']\n\n# Print the stock prices\nprint('APPL Stock Prices (Last 30 Days):')\nprint(appl_prices)\nprint('\\nNVDA Stock Prices (Last 30 Days):')\nprint(nvda_prices)", "dependencies_used_in_code": ["yfinance", "pandas"]}

[*********************100%%**********************]  1 of 1 completed
[*********************100%%**********************]  1 of 1 completed
APPL Stock Prices (Last 30 Days):
Date
2024-06-04    194.350006
2024-06-05    195.869995
2024-06-06    194.479996
2024-06-07    196.889999
2024-06-10    193.119995
2024-06-11    207.149994
2024-06-12    213.070007
2024-06-13    214.240005
2024-06-14    212.490005
2024-06-17    216.669998
2024-06-18    214.289993
2024-06-20    209.679993
2024-06-21    207.490005
2024-06-24    208.139999
2024-06-25    209.070007
2024-06-26    213.250000
2024-06-27    214.100006
2024-06-28    210.619995
2024-07-01    216.750000
2024-07-02    220.270004
2024-07-03    221.550003
Name: Close, dtype: float64

NVDA Stock Prices (Last 30 Days):
Date
2024-06-04    116.436996
2024-06-05    122.440002
2024-06-06    120.998001
2024-06-07    120.888000
2024-06-10    121.790001
2024-06-11    120.910004
2024-06-12    125.199997
2024-06-13    129.610001
2024-06-14    131.880005
2024-06-17    130.979996
2024-06-18    135.580002
2024-06-20    130.779999
2024-06-21    126.570000
2024-06-24    118.110001
2024-06-25    126.089996
2024-06-26    126.400002
2024-06-27    123.989998
2024-06-28    123.540001
2024-07-01    124.300003
2024-07-02    122.669998
2024-07-03    128.279999
Name: Close, dtype: float64
```


## License
This project is released under the MIT License.
