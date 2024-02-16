import sys
from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
from langchain.llms import Ollama
from tools import aider_coder_tool

load_dotenv()


hermes_llm = Ollama(model="openhermes")
coder_llm = Ollama(model="codellama:7b", temperature=0.8)

def update_code(filename):
    """
    Reviews the code in the provided file, provides a list of recommended
    changes to make to the code, and sends that list to aider to make the changes.

    Args:
        filename (str): The path to the file to be processed.

    Returns:
        str: A summary of the changes made to the code.

    """

    # Define the agents
    general_agent  = Agent(role='Requirements Manager',
      goal="""Help to communicate the changes that need to be made 
      to the code and summarize the work that was done.""",
      backstory="""You are an expert business analyst 
      and software QA specialist. You provide high quality, 
      thorough, insightful and actionable feedback via 
      detailed list of changes and actionable tasks.""",
      allow_delegation=False, 
      verbose=True,
      tools=[aider_coder_tool],
      llm=hermes_llm)
    
    code_review_agent = Agent(role='Software QA Engineer',
      goal="""To reivew the code in the provided file,
      create a detailed list of the changes to be made.
      These changes should include spelling fixes, formatting changes, and
      error fixes. Also suggest filling in any missing documentation.""",
      backstory="""You are an expert developer and software QA specialist.
      You are responsible for reviewing code in files provided to you and 
      excel in creating detailed lists of changes to be made.""",
      allow_delegation=False, 
      verbose=True,
      tools=[],
      llm=coder_llm)

    # read code from file
    code = ""
    with open(filename, 'r') as file:
        code = file.read()

    # define the tasks
    code_review_task = Task(description=f"""
			Review the following code and return a list of recommended changes:
                            
      <BEGIN_CODE>                
      {code}
      <END_CODE>

      DO NOT include examples of how to fix the issues.
      DO NOT change any of the content of the document or
      add content to it. It is critical to your task to
      only respond with a list of changes in the following format:

      Final Answer:
      <BEGIN_CHANGES>
      [insert your response here]
      <END_CHANGES>

      Code review complete.
      """,
      agent=code_review_agent)  
    
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
            
      Return the result from the tool as your Final Answer in this format:

      Final Answer:
      <BEGIN_UPDATES>
      [Replace this with the result returned by the aider_coder_tool]
      <END_UPDATES>
			""",
      agent=general_agent)  
    
    summary_task = Task(description=f"""Summaize the updates that were applied
      to {filename} based on the output of the edit_file_task.""",
      agent=general_agent)
    
    file_edit_crew = Crew(tasks=[code_review_task, edit_file_task, summary_task], 
                          agents=[general_agent,code_review_agent], 
                          process=Process.sequential)
    
    result = file_edit_crew.kickoff()

    return result


# If called directly from the command line take the first argument as the filename
if __name__ == "__main__":

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        processed_document = update_code(filename)
        print(processed_document)


