import os
from langchain.tools import tool
import sys
import openai
from aider.coders import Coder
from aider import  models

@tool("aider_coder_tool")
def aider_coder_tool(file_path_and_instructions: str) -> str:
    """
    A tool to edit files based on the provided instructions.

    Parameters:
    - file_path_and_instructions:  The changes to make to the 
    file and the path to the file to be edited.

    This string should be in the format "<file_path>|<instructions>".
    
    Returns:
    - result: The status of the edit.
    """

    file_path, instructions = file_path_and_instructions.split("|")

    print("\n\nEditing file...\n\n" + file_path)

    result = None
    try:
        client = openai.OpenAI(api_key=os.environ.get("AIDER_OPENAI_API_KEY", 
                                    os.environ["OPENAI_API_KEY"]), 
                        base_url=
                        os.environ.get("AIDER_OPENAI_API_BASE_URL", 
                        os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1")))

        model_name = os.environ.get("AIDER_MODEL", "gpt-3.5-turbo") 

        model =  models.Model.create(model_name, client)
        # Create a Coder object with the file to be updated
        coder = Coder.create(client=client, main_model=model, fnames=[file_path], 
                             auto_commits=False, pretty=False, stream=False)

        # Execute the instructions on the file
        result = coder.run(instructions)
        #print(result)
        
        return result
    except Exception as this_exception:
        print(f"File Edit Exception: {this_exception}", file=sys.stderr)
        return f"""Final Answer: There was an error when 
            editing the file:\n\n {str(this_exception)}"""
   
