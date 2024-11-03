from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from langchain_community.agent_toolkits.file_management.toolkit import FileManagementToolkit
from tools.browser_tools import BrowserTools
from tools.file_tools import FileTools
from tools.search_tools import SearchTools
from tools.template_tools import TemplateTools
import json
import ast

from dotenv import load_dotenv
load_dotenv()


@CrewBase
class ExpandIdeaCrew:
    """ExpandIdea crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def senior_idea_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_idea_analyst'],
            allow_delegation=False,
            tools=[
            SearchTools.search_internet,
            BrowserTools.scrape_and_summarize_website],
            verbose=True
        )
    
    @agent
    def senior_strategist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_strategist'],
            allow_delegation=False,
            tools=[
            SearchTools.search_internet,
            BrowserTools.scrape_and_summarize_website,],
            verbose=True
        )
    
    @task
    def expand_idea(self) -> Task: 
        return Task(
            config=self.tasks_config['expand_idea_task'],
            agent=self.senior_idea_analyst_agent(),
        )
    
    @task
    def refine_idea(self) -> Task: 
        return Task(
            config=self.tasks_config['refine_idea_task'],
            agent=self.senior_strategist_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )

@CrewBase
class ChooseTemplateCrew:

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    toolkit = FileManagementToolkit(
      root_dir='workdir',
      selected_tools=["read_file", "list_directory"]
    )

    @agent
    def senior_react_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_react_engineer'],
            allow_delegation=False,
            tools=[
          SearchTools.search_internet,
          BrowserTools.scrape_and_summarize_website,
          TemplateTools.learn_landing_page_options,
          TemplateTools.copy_landing_page_template_to_project_folder,
          FileTools.write_file
        ] + self.toolkit.get_tools(),
            verbose=True
        )
    
    
    @task
    def choose_template(self) -> Task: 
        return Task(
            config=self.tasks_config['choose_template_task'],
            agent=self.senior_react_engineer_agent(),
        )
        
    @task
    def update_page(self) -> Task: 
        return Task(
            config=self.tasks_config['update_page_task'],
            agent=self.senior_react_engineer_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
    
    
@CrewBase
class CreateContentCrew:

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    toolkit = FileManagementToolkit(
      root_dir='workdir',
      selected_tools=["read_file", "list_directory"]
    )

    @agent
    def senior_content_editor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_content_editor'],
            allow_delegation=False,
            tools=[
            ],
            verbose=True
        )
    
    @agent
    def senior_react_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_react_engineer'],
            allow_delegation=False,
            tools=[
                SearchTools.search_internet,
                BrowserTools.scrape_and_summarize_website,
                TemplateTools.learn_landing_page_options,
                TemplateTools.copy_landing_page_template_to_project_folder,
                FileTools.write_file
                ] + self.toolkit.get_tools(),
            verbose=True
        )
    
    @task
    def create_content(self) -> Task: 
        return Task(
            config=self.tasks_config['component_content_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    @task
    def update_component(self) -> Task: 
        return Task(
            config=self.tasks_config['update_component_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    
    @task
    def qa_component(self) -> Task: 
        return Task(
            config=self.tasks_config['qa_component_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
    
class LandingPageCrew():
    def __init__(self, idea):
        self.idea = idea
    
    def run(self):
        expanded_idea= self.runExpandIdeaCrew(self.idea)
            
        components_paths_list = self.runChooseTemplateCrew(expanded_idea)
            
        self.runCreateContentCrew(components_paths_list, expanded_idea)
    
    def runExpandIdeaCrew(self,idea):
        inputs1 = {
                "idea": str(idea)
        }
        expanded_idea= ExpandIdeaCrew().crew().kickoff(inputs=inputs1)
        return str(expanded_idea)

    def runChooseTemplateCrew(self, expanded_idea):
        inputs2={
            "idea": expanded_idea
        }
        components = ChooseTemplateCrew().crew().kickoff(inputs=inputs2)
        components= str(components)
        
        components = components.replace("\n", "").replace(" ",
                                                        "").replace("```","").replace("\\", "")
        
        # Convert the string to a Python list
        try:
            components_paths_list = ast.literal_eval(components)  # Safely parse the string
        except Exception as e:
            print(f"Error parsing the string: {e}")
            components_paths_list = []
        result= json.dumps(components_paths_list,indent=4)

        return json.loads(result)

    def runCreateContentCrew(self,components, expanded_idea):

        for component_path in components:
            file_content = open(
            f"./workdir/{component_path.split('./')[-1]}",
            "r"
        ).read()
            inputs3={
            "component": component_path,
            "expanded_idea": expanded_idea,
            "file_content": file_content
            }

            CreateContentCrew().crew().kickoff(inputs=inputs3)

    

    