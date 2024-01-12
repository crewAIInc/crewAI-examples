import sys
from crewai import Agent, Task
import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.chat_models.openai import ChatOpenAI
from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException

load_dotenv()

default_model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")


defalut_llm = ChatOpenAI(openai_api_base=os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
                        openai_api_key=os.environ.get("OPENAI_API_KEY"),
                        temperature=0.1,                        
                        model_name=os.environ.get("MODEL_NAME", "gpt-3.5-turbo"),
                        top_p=0.3)


@tool("markdown_validation_tool")
def markdown_validation_tool(file_path: str) -> str:
    """
    A tool to review files for markdown syntax errors.

    Parameters:
    - file_path: The path to the markdown file to be reviewed.

    Returns:
    - validation_results: A list of validation results 
    and suggestions on how to fix them.
    """
    
    print("\n\nValidating Markdown syntax...\n\n" + file_path)

    scan_result = None
    try:
        scan_result = PyMarkdownApi().scan_path(file_path)
        results = str(scan_result)
        print(results)
        syntax_validator_agent = Agent(role='Syntax Validator',
                                backstory="""You are an expert markdown validator. 
								You are an expert in formatting and structure. 
								You following formatting guidelines strictly.""",
                                goal="""
                                Provide a detailed list of the provided markdown 
                                linting results. Give a summary with actionable 
								tasks to address the validation results. Write your 
								response as if you were handing it to a developer 
								to fix the issues.
                                DO NOT provide examples of how to fix the issues.
								""", 
                                allow_delegation=False, 
                                verbose=True,
                                llm=defalut_llm)

        fix_syntax_task = Task(description="""Give a detailed list of the 
                               validation results below. Be sure to to include 
                               suggestions on how to fix the issues.
                               \n\nValidation Results:\n\n""" + results, 
                            agent=syntax_validator_agent)
            
        updated_markdown = fix_syntax_task.execute()

        return updated_markdown  # Return the reviewed document
    except PyMarkdownApiException as this_exception:
        print(f"API Exception: {this_exception}", file=sys.stderr)
        return f"API Exception: {str(this_exception)}"
    


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
                    goal="""To use the available tools to provide 
					execellent feedback to the team members.""",
                    backstory="""You are an expert business analyst 
					and software QA specialist. You provide high quality, 
                    thorough, insightful and actionable feedback.""",
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

			Collect the final answer from the syntax review tool 
			and then summarize it into a list of changes
			the developer should make to the document.
			
			If you already know the answer or if you do not need 
			to use a tool, return it as your Final Answer.""",
             agent=general_agent)
    
    updated_markdown = syntax_review_task.execute()

    return updated_markdown


processed_document = process_markdown_document("README.md")
print(processed_document)

# If called directly from the command line take the first argument as the filename
if __name__ == "__main__":

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        processed_document = process_markdown_document(filename)
        print(processed_document)




### Example Validation Results

##ikawrakow/open-hermes-2.5-mistral-7b-quantized-gguf/oh-2.5-m7b-q51.gguf
        
# model_name="oh-2.5m7b-q51",
# temperature=0.1,           
# top_p=0.3

# Here is a list of changes that the developer should make to the README.md file based 
# on the validation results from the markdown_validation_tool:

# 1. Add a # at the beginning of the first line to make it a 
# level 1 heading (e.g., "# My Project").
# 2. Break line 3 into two or more shorter lines, 
# as it is currently too long (127 characters).
# 3. Break line 7 into two or more shorter lines, 
# as it is currently too long (94 characters).
# 4. Break line 44 into multiple shorter lines or rephrase the content to 
# make it more concise, as it is extremely long (234 characters).
# 5. Repeat steps 1-4 for the remaining PyMarkdownScanFailure 
# entries in the validation results list.
# 6. Ensure that the README.md file follows proper Markdown syntax 
# and is well-structured, with appropriate headings, paragraphs, and lists as needed.
# 7. Add a brief introduction to the project at the beginning of the README.md file, 
# explaining its purpose and any key features or functionalities.
# 8. Review the overall readability and clarity of the README.md file, 
# making adjustments as necessary to ensure it is easy for others to understand and navigate.

## TheBloke/dolphin-2.6-mistral-7b-dpo.Q4_K_M.gguf        
# model_name="dolphin-2.6-mistral-dpo-7b-q4_k_m",
# temperature=0.1,           
# top_p=0.3
        
# The markdown validation tool has identified three issues in your README.md file. 
# Here's a summary of the changes you should make:

# 1. Add a first-line heading, such as `# Heading`, at the beginning of the README.md 
# file to comply with Rule ID: MD041.
# 2. Break long lines into shorter ones to ensure they don't exceed 80 characters. 
# You can use soft wraps or add line breaks where necessary. 
# This will help you adhere to Rule ID: MD013.
# 3. Review each line in the README.md file and ensure they don't exceed 80 characters. 
# If necessary, break up long lines or rephrase sentences to fit within the character 
# limit. This will also help you comply with Rule ID: MD013.