# CrewAI flight search (using Browserbase)

The following is a multi-task, multi-agent, multi-tool example for AI-based flight search using Skyscanner and Browserbase.

> [!TIP]
> [Browserbase](https://browserbase.com) is used to pre-render JavaScript pages, avoid IP blocks and captchas. As you will see in the example, AI-agents are especially useful for fetching content not available via APIs.

## Installation

### Setup

Install the required dependencies by running the following command:

```
pip install crewai 'crewai[tools]' html2text playwright dotenv
```

Set the required environment variables in a `.env` file:

```
OPENAI_API_KEY=
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=
```

Optional, but recommended. Set a different model type in CrewAI to avoid token size limits:

```
export OPENAI_MODEL_NAME=gpt-4-turbo
```

### Running the Demo

Start `main.py` script using Python, followed by your trip request:

```
python3 main.py "Sofia to Berlin one-way on 26th May"
```

Example output:

```
Here are our top 5 picks from Sofia to Berlin on 2nd July 2024:

1. **Ryanair**
   - Departure: 21:35
   - Arrival: 22:50
   - Duration: 2 hours 15 minutes
   - Layovers: Direct
   - Price: $18
   - Booking: [Ryanair](https://www.skyscanner.net/transport/flights/sof/ber/240702/0/config/16440-2407022135--31915-0-9828-2407022250?currency=USD)
...
```

## Guide

Explaining how to reproduce the example step-by-step.

### Agents, Tasks and Crews

1. Import the required dependencies:

```python
import sys
import os
from crewai import Crew, Process, Task, Agent
from crewai_tools import tool
from playwright.sync_api import sync_playwright
from html2text import html2text
from time import sleep
from typing import Optional
```

2. Create a flight agent for searching flights:

```python
flights_agent = Agent(
    role="Flights",
    goal="Search flights",
    backstory="I am an agent that can search for flights.",
    verbose=True,
    tools=[skyscanner, browserbase],
    allow_delegation=False,
)
```

2. Create a summarizer agent for summarizing outputs:

```python
summarize_agent = Agent(
    role="Summarize",
    goal="Summarize content",
    backstory="I am an agent that can summarize text.",
    verbose=True,
    allow_delegation=False,
)
```

3. Specify a task for searching flights according to criteria, including an output example:

```python
output_search_example = """
Here are our top 5 flights from Sofia to Berlin on 24th May 2024:

1. Bulgaria Air: Departure: 14:45, Arrival: 15:55, Duration: 2 hours 10 minutes, Layovers: Munich, 2 hours layover, Price: $123, Details: https://www.skyscanner.net/transport/flights/sof/ber/240524/240526/config/16440-2405241445--32474-0-9828-2405241555|9828-2405262255--32474-0-16440-2405270205
"""

search_task = Task(
    description=(
        "Search flights according to criteria {request}. Current year: {current_year}"
    ),
    expected_output=output_search_example,
    agent=flights,
)
```

4. Specify a task for fetching each flight for retrieving the booking links:

> [!TIP]
> CrewAI Agent is able to automatically loop each flight from the previous task to retrieve the booking information

```python
output_result_example = """
Here are our top 5 picks from Sofia to Berlin on 24th May 2024:

1. Bulgaria Air:
   - Departure: 14:45
   - Arrival: 15:55
   - Duration: 2 hours 10 minutes
   - Layovers: Munich, 2 hours layover
   - Price: $123
   - Booking: [MyTrip](https://www.skyscanner.net/transport_deeplink/4.0/UK/en-GB/GBP/ctuk/1/16440.9828.2024-05-26/air/trava/flights?itinerary=flight|-32474|319|16440|2024-05-26T21:05|9828|2024-05-26T22:15|130|-|-|-&carriers=-32474&operators=-32474&passengers=1&channel=website&cabin_class=economy&fps_session_id=20287887-26ad-45dc-b225-28fb4b9d8357&ticket_price=126.90&is_npt=false&is_multipart=false&client_id=skyscanner_website&request_id=4b423165-9b7b-4281-9596-cfcd6b0bb4e0&q_ids=H4sIAAAAAAAA_-NS52JJLinNFmLh2NHAKMXM8cRHoeH7yU1sRkwKjEWsqXm67k5VzO5OAQASECl8KQAAAA|8257781087420252411|2&q_sources=JACQUARD&commercial_filters=false&q_datetime_utc=2024-05-22T13:45:58&pqid=true&booking_panel_option_guid=dfb1f593-22dc-4565-8540-5f4f70979b9b&index=0&isbp=1&posidx=0&qid=16440-2405262105--32474-0-9828-2405262215&sort=BEST&stops=0&tabs=CombinedDayView&pre_redirect_id=7cdb112a-3842-4a51-b228-1cbcbc4c8094&redirect_id=a8541976-84a8-4161-849c-c7a6343125ae&is_acorn_referral=true)
"""

search_booking_providers_task = Task(
    description="Load every flight individually and find available booking providers",
    expected_output=output_result_example,
    agent=flights,
)
```

5. Initialize new crew with agents and tasks:

```python
crew = Crew(
    agents=[flights_agent, summarize_agent],
    tasks=[search_task, search_booking_providers_task],
    max_rpm=100,
)
```

6. Kick off the crew and print the result:

```python
result = crew.kickoff(
    inputs={
        "request": "Flights from Sofia to Berlin on 2th July",
        "current_year": 2024,
    }
)

print(result)
```

### Bring up the tools

1. Create a Skyscanner tool to generate a valid Skyscanner URL for the given query

```python
@tool("SkyScanner tool")
def skyscanner(
    departure: str, destination: str, date: int, return_date: Optional[int] = 0
) -> str:
    """
    Generates a SkyScanner URL for flights between departure and destination on the specified date.

    :param departure: The IATA code for the departure airport (e.g., 'sof' for Sofia)
    :param destination: The IATA code for the destination airport (e.g., 'ber' for Berlin)
    :param date: The date of the flight in the format 'yymmdd'
    :return_date: Only for two-way tickets. The date of return flight in the format 'yymmdd'
    :return: The SkyScanner URL for the specified flight search
    """
    return f"https://www.skyscanner.net/transport/flights/{departure}/{destination}/{date}/{return_date}?currency=USD"
```

2. Create a browserbase tool to open webpages using a headless web browser

```python
@tool("Browserbase tool")
def browserbase(url: str):
    """
    Loads a URL using a headless webbrowser

    :param url: The URL to load
    :return: The text content of the page
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(
            "wss://connect.browserbase.com?enableProxy=true&apiKey="
            + os.environ["BROWSERBASE_API_KEY"]
        )
        context = browser.contexts[0]
        page = context.pages[0]
        page.goto(url)

        # Wait for async content of the page to load
        sleep(5)

        # Optionally take a screenshot to debug current page
        # page.screenshot(path="screenshot.png")

        content = html2text(page.content())
        browser.close()
        return content
```
