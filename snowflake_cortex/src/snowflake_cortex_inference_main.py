# Author: Sean Iannuzzi
# Created: January 13, 2024

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
import litellm
from snowflake_cortex_inference_handler import SnowflakeCortexInferenceService
import json

load_dotenv()

litellm.set_verbose=True

#following example is using the default cortex service created in snowflake for inference 
snowflakeServicePayload = {
        "model": "[FOUNDATION_MODEL_NAME]", #mistral-large, llama3, etc
        "messages": [
            {
                "content": "<prompt>"
            }
        ],
        "top_p": 0,
        "temperature": 0
}

snowflake_cortex_inference_llm = SnowflakeCortexInferenceService(model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
    base_url = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
    snowflakeAccount=os.environ.get("SNOWFLAKE_ACCOUNT"),
    snowflakeServiceUser=os.environ.get("SNOWFLAKE_SERVICE_USER"),
    snowflakePromptTemplate = snowflakeServicePayload
    )

litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
        {"provider": "snowflake-cortex-inference-service", "custom_handler": snowflake_cortex_inference_llm}
        ]

custom_llm = LLM(
    model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
    api_base = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY")
)

#Create a researcher agent
researcher = Agent( 
   role='Senior Researcher',
   goal='You are looking for information about the oceean',
   verbose=True,
   llm=custom_llm, # 👈 KEY STEP - REGISTER HANDLER
   backstory='You are just looking for some fish that live in the ocean',
   max_iter=1,
)

# Task for the researcher
research_task = Task(
  description='Make a single call hoping to get a similar response to ocean information but also include reference links',
  expected_output='ocean information',
  agent=researcher  # Assigning the task to the researcher
)

#Instantiate your crew
tech_crew = Crew(
  agents=[researcher],
  tasks=[research_task],
  process=Process.sequential  # Tasks will be executed one after the other
)

# # # Begin the task execution
result = tech_crew.kickoff()

#if the agent is failing to complete the task, you can print the result to see what is going wrong
#print("\n--- Execution Result ---")
#print(result)

print("\n--- Summarizing results please wait ---")

response = custom_llm.call(messages=[{"role": "user", "content": f"Summarize this information for me but also include the links {result}"}])

# summarize the results - could have added another task, but this is a simple way to show the results
print("\n--- Summarized Results ---")
print(response)


