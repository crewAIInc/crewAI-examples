from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, after_kickoff, agent, crew, task
from crewai_tools import SerperDevTool
from crewai_tools import ScrapeWebsiteTool
from crewai.crews.crew_output import CrewOutput


from trip_planner.tools.flight_search_tool import FlightSearchTool
from trip_planner.tools.accommodation_search_tool import AccommodationSearchTool

@CrewBase
class TripPlanner():
    """TripPlanner crew"""

    @after_kickoff
    def process_results(self, result: CrewOutput) -> CrewOutput:
        print(result.tasks_output)

        outputs = {}

        for task_output in result.tasks_output:
            outputs[task_output.name] = task_output
        
        final_result = f"""
{outputs['report_generation_task']}
***

# Travel Options

{outputs['travel_options_task']}

***

# Accommodation

{outputs['accommodation_search_task']}

***

# Daily Itinerary

{outputs['itinerary_planning_task']}

        """

        with open('trip_report.md', 'w') as f:
            f.write(final_result)

        return final_result

    @agent
    def destination_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['destination_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @agent
    def travel_options_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_options_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), FlightSearchTool()],
        )

    @agent
    def accommodation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['accommodation_researcher'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), AccommodationSearchTool()],
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_planner'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )
    
    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
        )


    @task
    def destination_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['destination_research_task'],
        )

    @task
    def travel_options_task(self) -> Task:
        return Task(
            config=self.tasks_config['travel_options_task'],
            output_file='1_travel_options.md',
        )

    @task
    def accommodation_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['accommodation_search_task'],
            output_file='2_accommodation.md',
        )

    @task
    def itinerary_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_planning_task'],
            output_file='3_itinerary_plan.md',
        )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='4_trip_report.md',
        )


    @crew
    def crew(self) -> Crew:
        """Creates the TripPlanner crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
