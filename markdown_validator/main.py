import sys
from crewai import Agent, Task
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from MarkdownTools import markdown_validation_tool
import agentops

load_dotenv()
agentops.init()

defalut_llm = ChatOpenAI(openai_api_base=os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
                        openai_api_key=os.environ.get("OPENAI_API_KEY"),
                        temperature=0.1,                        
                        model_name=os.environ.get("MODEL_NAME", "gpt-3.5-turbo"))



def process_markdown_document(filename):
    """
    Processes a markdown document by reviewing its syntax validation 
    results and providing feedback on necessary changes.

    Args:
        filename (str): The path to the markdown file to be processed.

    Returns:
        str: The list of recommended changes to make to the document.

    """

    # Define general agent
    general_agent  = Agent(role='Requirements Manager',
                    goal="""Provide a detailed list of the markdown 
                            linting results. Give a summary with actionable 
                            tasks to address the validation results. Write your 
                            response as if you were handing it to a developer 
                            to fix the issues.
                            DO NOT provide examples of how to fix the issues or
                            recommend other tools to use.""",
                    backstory="""You are an expert business analyst 
					and software QA specialist. You provide high quality, 
                    thorough, insightful and actionable feedback via 
                    detailed list of changes and actionable tasks.""",
                    allow_delegation=False, 
                    verbose=True,
                    tools=[markdown_validation_tool],
                    llm=defalut_llm)


    # Define Tasks Using Crew Tools
    syntax_review_task = Task(description=f"""
			Use the markdown_validation_tool to review 
			the file(s) at this path: {filename}
            
			Be sure to pass only the file path to the markdown_validation_tool.
			Use the following format to call the markdown_validation_tool:
			Do I need to use a tool? Yes
			Action: markdown_validation_tool
			Action Input: {filename}

			Get the validation results from the tool 
			and then summarize it into a list of changes
			the developer should make to the document.
            DO NOT recommend ways to update the document.
            DO NOT change any of the content of the document or
            add content to it. It is critical to your task to
            only respond with a list of changes.
			
			If you already know the answer or if you do not need 
			to use a tool, return it as your Final Answer.""",
            agent=general_agent,
            expected_output="")
    
    updated_markdown = syntax_review_task.execute()

    return updated_markdown

# If called directly from the command line take the first argument as the filename
if __name__ == "__main__":

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        processed_document = process_markdown_document(filename)
        print(processed_document)

    else:
        filename = "README.md"
        processed_document = process_markdown_document(filename)
        print(processed_document)

