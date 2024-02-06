import sys
from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
from langchain.llms import Ollama
from tools import aider_coder_tool

load_dotenv()


hermes_llm = Ollama(model="openhermes")
coder_llm = Ollama(model="deepseek-coder")

def update_code(filename):
    """
    Reviews the code in the provided file, provides a list of recommended
    changes to make to the code, and sends that list to aider to make the changes.

    Args:
        filename (str): The path to the file to be processed.

    Returns:
        str: A summary of the changes made to the code.

    """

    # Define general agent
    general_agent  = Agent(role='Requirements Manager',
      goal="""Provide a detailed list of the provided markdown 
              linting results. Give a summary with actionable 
              tasks to address the validation results. Write your 
              response as if you were handing it to a developer 
              to fix the issues.
              DO NOT provide examples of how to fix the issues.""",
      backstory="""You are an expert business analyst 
      and software QA specialist. You provide high quality, 
      thorough, insightful and actionable feedback via 
      detailed list of changes and actionable tasks.""",
      allow_delegation=False, 
      verbose=True,
      tools=[],
      llm=hermes_llm)
    
    file_editor_agent = Agent(role='Software QA Engineer',
                    goal=f"""To reivew the code in the provided file,
                    create a detailed list of the changes to be made,
                    and provide the list to aider to make the changes to {filename}.""",
                    backstory="""You are an expert developer and software QA specialist.
                    You are responsible for reviewing code in files provided to you and 
                    excel in creating detailed lists of changes to be made.""",
                    allow_delegation=False, 
                    verbose=True,
                    tools=[aider_coder_tool],
                    llm=hermes_llm)


    # Define Tasks Using Crew Tools
    # syntax_review_task = Task(description=f"""
    # 	Use the markdown_validation_tool to review 
    # 	the file(s) at this path: {filename}            
    # 	Be sure to pass only the file path to the markdown_validation_tool.
    # 	Use the following format to call the markdown_validation_tool:
    # 	Do I need to use a tool? Yes
    # 	Action: markdown_validation_tool
    # 	Action Input: {filename}

    # 	Get the validation results from the tool 
    # 	and then summarize it into a list of changes
    # 	the developer should make to the document.
    #         DO NOT include examples of how to fix the issues.
    #         DO NOT change any of the content of the document or
    #         add content to it. It is critical to your task to
    #         only respond with a list of changes.
      
    # 	If you already know the answer or if you do not need 
    # 	to use a tool, return it as your Final Answer.""",
    #          agent=general_agent)


    # read code from file
    code = ""
    with open(filename, 'r') as file:
        code = file.read()

    code_review_task = Task(description=f"""
			Review the following code and return a list of recommended changes:
                            
      <BEGIN_CODE>                
      {code}
      <END_CODE>

      DO NOT include examples of how to fix the issues.
      DO NOT change any of the content of the document or
      add content to it. It is critical to your task to
      only respond with a list of changes in the following format:

      Final answer:
      <BEGIN_CHANGES>
      [insert your response here]
      <END_CHANGES>
      """,
      agent=file_editor_agent)  
    
    edit_file_task = Task(description=f"""
			Use the changes provided to you to edit the specified 
			the file(s) at this path: {filename}
            
      Once the file is edited, return the result as your Final Answer.
      If there is an error while editing a file, you should inform 
      the team that you cannot currently edit the file.
      If there are no changes needed to the file,
      your taks is complete, and you should inform the team.

			Be sure to pass only the file path and the complete set of changes
      you receive to the aider_coder_tool.

			Use the following format to call the aider_coder_tool:
			Do I need to use a tool? Yes
			Action: aider_coder_tool
			Action Input: {filename}|<the full set of instructions>
			""",
      agent=file_editor_agent)  
    
    file_edit_crew = Crew(tasks=[code_review_task, edit_file_task], 
                          agents=[general_agent,file_editor_agent], 
                          process=Process.sequential)
    
    result = file_edit_crew.kickoff()

    return result


# If called directly from the command line take the first argument as the filename
if __name__ == "__main__":

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        processed_document = update_code(filename)
        print(processed_document)


