# Author: Sean Iannuzzi
# Created: January 10, 2024
# Updated: January 13, 2024
# Notes:
# - Added payload as a parameter

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
import litellm
from snowflake_cortex_custom_handler import SnowflakeCortexCustomServiceLLM
import time
import json
from datetime import datetime, timedelta

load_dotenv()

litellm.set_verbose=True

#example service payload - you will want to customize this based on your specific cortex service 
snowflakeServicePayload = {
    "query": "",
    "name": "[YOUR_CORTEX_SERVICE_NAME]",
    "search_column": "INDEX_TEXT",
    "columns": ["FIELD1, FIELD2, FIELD3"],
    "attribute_columns": [],
    "target_lag": {
        "type": "USER_DEFINED",
        "seconds": 86400
    },
    "warehouse": "[YOUR_WAREHOUSE]",
    "definition": "SELECT [FIELD1, FIELD2, FIELD3] FROM [YOUR_DATABASE_NAME]",
    "comment": None,
    "created_on": datetime.utcnow().isoformat(),
    "database_name": "[YOUR_DATABASE_NAME]",
    "schema_name": "[YOUR_SCHEMA_NAME]",
    "source_data_num_rows": 400,
    "data_timestamp": None,
    "indexing_state": "ACTIVE",
    "serving_state": "ACTIVE",
    "indexing_error": None,
    "serving_data_bytes": 1297920
}

snowflake_custom_cortex_llm = SnowflakeCortexCustomServiceLLM(model="snowflake-cortex-custom-service-llm/snowflake-cortex-custom-service-llm",
    base_url = os.environ.get("SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
    snowflakeAccount=os.environ.get("SNOWFLAKE_ACCOUNT"),
    snowflakeServiceUser=os.environ.get("SNOWFLAKE_SERVICE_USER"),
    snowflakePromptTemplate = snowflakeServicePayload
    )

litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
        {"provider": "snowflake-cortex-custom-service-llm", "custom_handler": snowflake_custom_cortex_llm}
        ]

custom_llm = LLM(
    model="snowflake-cortex-custom-service-llm/snowflake-cortex-custom-service-llm",
    api_base = os.environ.get("SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
)

response = custom_llm.call(messages=[{"role": "user", "content": "Tell me about the ocean"}])
print(response)

#Create a researcher agent
researcher = Agent( 
   role='Senior Researcher',
   goal='You are looking for cases from a ticketing system to help you with your research',
   verbose=True,
   llm=custom_llm, # 👈 KEY STEP - REGISTER HANDLER
   backstory='You are just looking for a list of cases or case related information',
   max_iter=1,
)

# Task for the researcher
research_task = Task(
  description='Make a single call hoping to get a similar response to case information',
  expected_output='case information',
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
print("\n--- Execution Result ---")
print(result)


