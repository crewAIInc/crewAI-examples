import sys
from crewai import Crew, Process, Task, Agent
from bb import browserbase
from skyscanner import skyscanner

output_search_example = """
Here are our top 5 flights from Sofia to Berlin on 24th May 2024:

1. Bulgaria Air: Departure: 14:45, Arrival: 15:55, Duration: 2 hours 10 minutes, Layovers: Munich, 2 hours layover, Price: $123, Details: https://www.skyscanner.net/transport/flights/sof/ber/240524/240526/config/16440-2405241445--32474-0-9828-2405241555|9828-2405262255--32474-0-16440-2405270205
"""

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

flights = Agent(
    role="Flights",
    goal="Search flights",
    backstory="I am an agent that can search for flights.",
    verbose=True,
    tools=[skyscanner, browserbase],
    allow_delegation=False,
)

summarize_agent = Agent(
    role="Summarize",
    goal="Summarize content",
    backstory="I am an agent that can summarize text.",
    verbose=True,
    allow_delegation=False,
)

search_task = Task(
    description=(
        "Search flights according to criteria {request}. Current year: {current_year}"
    ),
    expected_output=output_search_example,
    agent=flights,
    human_input=False,  # Optional
)

search_providers = Task(
    description="Load every flight individually and find available booking providers",
    expected_output=output_result_example,
    agent=flights,
    human_input=False,
)

crew = Crew(
    agents=[flights, summarize_agent],
    tasks=[search_task, search_providers],
    process=Process.sequential,
    memory=False,
    cache=True,
    max_rpm=100,
)

result = crew.kickoff(
    inputs={
        "request": sys.argv[1] or "Flights from Sofia to Berlin on 2th July",
        "current_year": 2024,
    }
)

print(result)
