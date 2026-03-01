🚀 Snowflake Cortex Service Helpers for CrewAI and LiteLLM
This document introduces two helper classes to interact with Snowflake Cortex APIs for language model tasks. These classes streamline integration with both custom Cortex services and built-in foundation models deployed in Snowflake.

⚙️ 1. Snowflake Cortex Custom LLM Helper
The Snowflake Cortex Custom LLM Helper class is designed to integrate with custom Cortex services you’ve deployed in Snowflake. This class provides a flexible interface to connect with your custom APIs, handle requests, and manage configurations for completing language model tasks using CrewAI and LiteLLM.

🧩 Features
Custom Cortex Service Integration: Connect to your custom endpoints within Snowflake Cortex.
Flexible Configuration: Supports configurable parameters such as base_url, api_key, timeout, etc.
Dynamic JWT Authentication: Automates JWT token generation based on your private key, ensuring secure communication.
Token Counting: Built-in token counting to help manage large inputs efficiently.
Error Handling: Provides robust error handling and retries for API requests.

# Example Usage for a Snowflake Cortex Custom Service

# Initialize the Snowflake Cortex Custom Service LLM with the Snowflake API details
```python
snowflake_custom_cortex_llm = SnowflakeCortexCustomServiceLLM(model="snowflake-cortex-custom-service-llm/snowflake-cortex-custom-service-llm",
    base_url = os.environ.get("SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
    snowflakeAccount=os.environ.get("SNOWFLAKE_ACCOUNT"),
    snowflakeServiceUser=os.environ.get("SNOWFLAKE_SERVICE_USER"),
    snowflakePromptTemplate = snowflakeServicePayload
    )
```
# Register the Snowflake Cortex Custom Service LLM as a provider in LiteLLM
```python
litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
        {"provider": "snowflake-cortex-custom-service-llm", "custom_handler": snowflake_custom_cortex_llm}
        ]
```
# Create an LLM instance using the Snowflake Cortex Custom Service LLM
```python
custom_llm = LLM(
    model="snowflake-cortex-custom-service-llm/snowflake-cortex-custom-service-llm",
    api_base = os.environ.get("SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
)
```
# Use the Snowflake Cortex Custom Service LLM to generate a response
```python
response = snowflakecortex_custom_llm.completion(messages=[{"role": "user", "content": "Show me information about cases"}])
```
# Use the liteLLM to generate a response
```python
response = custom_llm.call(messages=[{"role": "user", "content": "Show me information about cases"}])
```

🧩2. Snowflake Cortex Inference Service Helper
The Snowflake Cortex Inference Service Helper class enables interaction with Snowflake's built-in foundation models (e.g., GPT, Mistral) through their Inference Service API. This class simplifies access to pre-deployed models without needing to manage your own custom endpoints.

🧰 Features
Foundation Model Access: Use pre-deployed LLMs provided by Snowflake, such as GPT, Mistral, and more.
Token Management: Automatically tracks prompt tokens and completion tokens for API responses.
Easy Configuration: Minimal setup required with base_url, api_key, and model selection.
Secure JWT Authentication: Supports JWT-based authorization for secure requests.

# Example Usage for Snowflake Cortex Inference Services
# Initialize the Snowflow Cortext Inference Service with the Snowflake API details
```python
snowflake_cortex_inference_llm = SnowflakeCortexInferenceService(model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
    base_url = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
    snowflakeAccount=os.environ.get("SNOWFLAKE_ACCOUNT"),
    snowflakeServiceUser=os.environ.get("SNOWFLAKE_SERVICE_USER"),
    snowflakePromptTemplate = snowflakeServicePayload
    )
```
# Register the Snowflake Cortext Inference Service as a custom provider in LiteLLM
```python
litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
        {"provider": "snowflake-cortex-inference-service", "custom_handler": snowflake_cortex_inference_llm}
        ]
```
# Create a Custom LLM instance using the Snowflake Cortext Inference Service
```python
custom_llm = LLM(
    model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
    api_base = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
    api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY")
)
```
# Use the Snowflake Cortex Custom Service to generate a response
```python
response = snowflake_cortex_inference_llm.completion(messages=[{"role": "user", "content": "Tell me about the ocean"}])
```
# Use the liteLLM to generate a response
```python
response = custom_llm.call(messages=[{"role": "user", "content": "Tell me about the ocean"}])
```

✅ When to Use Each Helper Class:
Use Case 1		
You have a custom Cortex service	

Helper Class
SnowflakeCortexCustomLLM	

Description
For integrating with your own deployed services.

Use Case 2
You want to use built-in models

Helper Class
SnowflakeCortexInferenceService

Description
For leveraging Snowflake’s foundation models.

# Register either Snowflake Cortex Custom or Inference Services with an Agent
```python
researcher = Agent( 
   role='Senior Researcher',
   goal='You are looking for cases from a ticketing system to help you with your research',
   verbose=True,
   llm=custom_llm, # 👈 KEY STEP - REGISTER HANDLER
   backstory='You are just looking for a list of cases or case related information',
   max_iter=1,
)
```
# Final Code with Task and Crew
```python
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
```

# To check the results of the Crew, Tasks and Agents
```python
#if the agent is failing to complete the task, you can print the result to see what is going wrong
print("\n--- Execution Result ---")
print(result)
```

Installation
Make sure to install the necessary dependencies before using the Snowflake Cortex Crew AI Helper Modules:

Notes
Make sure to set the environment variables:
SNOWFLAKE_ACCOUNT
SNOWFLAKE_SERVICE_USER
SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL
SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL
SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY
with the appropriate values for your Snowflake Cortex instance. 

You can modify the class to suit your needs, including adjusting request parameters, service payload and error handling.

## License
This project is released under the MIT License.