# Author: Sean Iannuzzi
# Created: January 13, 2024

import litellm
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse
import requests
import time
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator
from snowflake_cortex_service_custom_error import SnowflakeCortexCustomServiceError
from snowflake_auth_jwt_generator import JWTGenerator

"""
Snowflake Cortext Inference Service for Snowflake Cortex LLM Integration
This Snowflake Cortext Inference Service Class enables integration with Snowflake Cortex through their API endpoints. 
The implementation provides a flexible interface to connect to the Snowflake API, manage API requests, 
and handle the necessary configurations for completing language model tasks. 

Note: 
You could change this to inheret from BaseLLM instead of CustomLLM if you want to use the base class
for a more generic implementation.
"""
class SnowflakeCortexInferenceService(CustomLLM):
    """
    SnowflakeCortexInferenceService: A custom implementation of a Snowflake Cortext Inference Service 
    designed to integrate with the Snowflake API and be registered as a provider
    within LiteLLM and Crew AI agents.

    This class extends the base `CustomLLM` class to facilitate the integration of a custom language 
    model that interacts with the Snowflake Cortext Inference Service API. By defining a `custom_provider_map`, 
    this custom model can be invoked within Crew AI agents for specific tasks, leveraging flexible 
    configuration options such as `base_url`, `api_key`, and other model parameters. 

    The primary purpose of this Snowflake Cortext Inference Service is to enable communication 
    with the Snowflake Cortext Inference Service API, allowing the model to interact with Snowflake data,
    retrieve relevant insights, or perform specific queries as part of an AI-driven agent's workflow.

    Attributes:
        model (str): The model name or identifier to be used for generating responses.
        snowflakeAccount (str): The Snowflake account name for authentication and data access.
        snowflakeServiceUser (str): The Snowflake service user name for API access.
        snowflakePromptTemplate (str): The template for the Snowflake API request payload.
        timeout (Optional[Union[float, int]]): The maximum time to wait for the model's response.
        temperature (Optional[float]): Adjusts the creativity/randomness of the model's outputs.
        top_p (Optional[float]): Applies nucleus sampling to limit token choices based on cumulative probability.
        n (Optional[int]): The number of completions to generate for each request.
        stop (Optional[Union[str, List[str]]]): Defines one or more stop sequences to halt the model's output.
        max_completion_tokens (Optional[int]): Maximum token count for the completion response.
        max_tokens (Optional[int]): Total maximum token count for input and output combined.
        presence_penalty (Optional[float]): Encourages/discourages new token generation based on prior presence.
        frequency_penalty (Optional[float]): Discourages token repetition in generated text.
        logit_bias (Optional[Dict[int, float]]): Allows manipulation of token likelihoods.
        response_format (Optional[Dict[str, Any]]): Specifies the desired response format from the model.
        seed (Optional[int]): Seed for reproducibility of the model's behavior.
        logprobs (Optional[bool]): Whether to include log probabilities for the generated tokens.
        top_logprobs (Optional[int]): Number of top tokens with log probabilities to return.
        base_url (Optional[str]): The base URL for the model's API endpoint.
        api_version (Optional[str]): The version of the API to be used for the request.
        api_key (Optional[str]): The API key required for authentication.
        callbacks (List[Any]): List of callback functions for response handling or event monitoring.

    Methods:
        __init__(self, **kwargs): Initializes the custom LLM with the provided configuration options.

    Usage Example:
        # Initialize the custom LLM with the Snowflake API details
        snowflake_cortex_inference_llm = SnowflakeCortexInferenceService(model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
            base_url = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
            api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
            snowflakeAccount=os.environ.get("SNOWFLAKE_ACCOUNT"),
            snowflakeServiceUser=os.environ.get("SNOWFLAKE_SERVICE_USER"),
            snowflakePromptTemplate = snowflakeServicePayload
        )

        # Register the Snowflake Cortext Service custom LLM as a provider in LiteLLM
        litellm.custom_provider_map = [ # 👈 KEY STEP - REGISTER HANDLER
                {"provider": "snowflake-cortex-inference-service", "custom_handler": snowflake_cortex_inference_llm}
        ]

        # Create an LLM instance using the custom Snowflake Cortext Service LLM
        custom_llm = LLM(
            model="snowflake-cortex-inference-service/snowflake-cortex-inference-service",
            api_base = os.environ.get("SNOWFLAKE_CORTEXT_INFERENCE_LLM_BASE_URL"),
            api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY")
        )

        # Use the custom LLM to generate a response
        response = snowflake_cortex_inference_llm.completion(messages=[{"role": "user", "content": "Tell me about the ocean"}])

        # Use the liteLLM to generate a response
        response = custom_llm.call(messages=[{"role": "user", "content": "Tell me about the ocean"}])

    The SnowflakeCortexServiceLLM class is designed to integrate tightly with the Snowflake Cortex ServiceAPI, 
    allowing the model to access Snowflake data, process it, and return relevant results to the agent 
    or user. By registering the custom handler with `custom_provider_map`, this custom model 
    can be used within the LiteLLM framework and Crew AI agents, extending the capabilities 
    of AI-driven workflows and ensuring smooth interaction with Snowflake for data-driven tasks.
    """

    def __init__(
            self,
            model: str,
            snowflakeAccount: str,
            snowflakeServiceUser: str,
            snowflakePromptTemplate: str,
            privatekey_password: Optional[str] = None,
            timeout: Optional[Union[float, int]] = None,
            temperature: Optional[float] = None,
            top_p: Optional[float] = None,
            n: Optional[int] = None,
            stop: Optional[Union[str, List[str]]] = None,
            max_completion_tokens: Optional[int] = None,
            max_tokens: Optional[int] = None,
            presence_penalty: Optional[float] = None,
            frequency_penalty: Optional[float] = None,
            logit_bias: Optional[Dict[int, float]] = None,
            response_format: Optional[Dict[str, Any]] = None,
            seed: Optional[int] = None,
            logprobs: Optional[bool] = None,
            top_logprobs: Optional[int] = None,
            base_url: Optional[str] = None,
            api_version: Optional[str] = None,
            api_key: Optional[str] = None,
            callbacks: List[Any] = [],
            **kwargs,
        ):
            self.model = model
            self.snowflakeAccount = snowflakeAccount
            self.snowflakeServiceUser = snowflakeServiceUser
            self.snowflakePromptTemplate = snowflakePromptTemplate
            self.privatekey_password = privatekey_password
            self.timeout = timeout
            self.temperature = temperature
            self.top_p = top_p
            self.n = n
            self.stop = stop
            self.max_completion_tokens = max_completion_tokens
            self.max_tokens = max_tokens
            self.presence_penalty = presence_penalty
            self.frequency_penalty = frequency_penalty
            self.logit_bias = logit_bias
            self.response_format = response_format
            self.seed = seed
            self.logprobs = logprobs
            self.top_logprobs = top_logprobs
            self.base_url = base_url
            self.api_version = api_version
            self.api_key = api_key
            self.callbacks = callbacks
            self.context_window_size = 0
            self.kwargs = kwargs

            super().__init__()


    def call(self, *args, **kwargs) -> litellm.ModelResponse:
        """
        Executes the custom language model's API request and returns the response.

        This method is responsible for invoking the underlying model API (e.g., Snowflake, or any
        other model defined in the custom LLM) using the provided arguments and keyword arguments. 
        It processes the request, communicates with the appropriate external service (such as Snowflake API),
        and returns a response in the form of a `litellm.ModelResponse`.

        Parameters:
            *args: Variable positional arguments that can be passed to the underlying model API.
            **kwargs: Variable keyword arguments that can be passed to the underlying model API, 
                    including parameters like `timeout`, `temperature`, `api_key`, etc.

        Returns:
            litellm.ModelResponse: A response object that encapsulates the result of the model's API request, 
                                typically including fields such as the generated output, completion choices, 
                                and any additional metadata returned from the model API.
        """
        if callbacks is None:
            callbacks = []
        if callbacks and len(callbacks) > 0:
            self.set_callbacks(callbacks)

        # Call the completion method with the provided arguments and keyword arguments
        return self.completion(*args, **kwargs)

    def completion(self, *args, **kwargs) -> litellm.ModelResponse:
        """
        Handles the completion request for the custom language model via event-stream.

        This method is responsible for invoking the language model to generate completions based
        on the provided input arguments. It interfaces with the underlying model API (such as
        Snowflake API or any other custom model) to process the completion request, and returns
        the response encapsulated in a `litellm.ModelResponse`.

        Parameters:
            *args: Variable positional arguments that can be passed to the underlying model API.
            **kwargs: Variable keyword arguments that can be passed to the underlying model API, 
                      including parameters like `temperature`, `max_tokens`, `top_p`, and others.

        Returns:
            litellm.ModelResponse: A response object containing the model's completion result, 
                                  including the generated text, any choices, and other metadata 
                                  associated with the completion request.
        """    
        modelResponse = None

        try:
            payload = None

            # Try getting payload from kwargs first (if passed as a keyword argument)
            if "messages" in kwargs:
                self.snowflakePromptTemplate["messages"] = kwargs.get("messages", [])
                payload = self.snowflakePromptTemplate
            
            # If no payload found in kwargs, try getting it from args (if passed as a positional argument)
            elif args:
                payload = args[0]

            # If no payload found in either, raise an error
            if payload is None:
                raise SnowflakeCortexCustomServiceError(status_code=500, message="No payload provided")
                
            # Server URL only needs to be defined once
            server_url = self.base_url

            # Generate the bearer token
            bearerToken = JWTGenerator(self.snowflakeAccount, 
                self.snowflakeServiceUser, self.api_key.strip(), 
                self.privatekey_password, timedelta(minutes=59),
                timedelta(minutes=54)).get_token()

            # Format the private key 
            privateKeyPEMFormatted = (
                self.api_key
                .replace("-----BEGIN PRIVATE KEY-----", "")
                .replace("-----END PRIVATE KEY-----", "")
                .replace("\r\n", "")
                .replace("\n", "")
            )

            # Set the headers for the request
            headers = {
                "Authorization": f"Bearer {bearerToken}",
                "X-Snowflake-Private-Key": privateKeyPEMFormatted,
                "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT",
                "Content-Type": "application/json",       
                "Accept": "application/json"
            }

            # Make the POST request to the API with streaming enabled
            response = requests.post(server_url, headers=headers, json=payload, stream=True)

            # Check if the response is a valid event-stream
            if "text/event-stream" in response.headers.get("Content-Type"):

                # Initialize variables to accumulate content and token counts
                accumulated_content = ""
                total_prompt_tokens = 0
                total_completion_tokens = 0

                for line in response.iter_lines():
                    if line:  # Ignore empty lines
                        line_str = line.decode('utf-8')

                        if line_str.startswith("data:"):
                            event_data = line_str[len("data:"):].strip()  # Extract event data (JSON)
                            try:
                                parsed_data = json.loads(event_data)  # Parse as JSON

                                # Extract content from 'choices' and accumulate it
                                delta = parsed_data.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                accumulated_content += content

                                # Update token usage
                                usage = parsed_data.get('usage', {})
                                total_prompt_tokens += usage.get('prompt_tokens', 0)
                                total_completion_tokens += usage.get('completion_tokens', 0)

                            except json.JSONDecodeError:
                                print("Error decoding event data:", event_data)

                # this is only needed for testing when you 
                # need the answer returned after a single request
                #final_response = f"Final Answer: {accumulated_content.strip()}"
                
                final_response = accumulated_content.strip()

                # Return the response data wrapped in the ModelResponse
                json_response = {
                    "id": f"chatcmpl-{self.generate_unique_id()}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": self.model,
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "index": 0,
                            "message": {
                                "content": final_response,
                                "role": "assistant"
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens
                    }
                }
                # Construct the final response
                modelResponse = litellm.ModelResponse(
                    object=json_response['object'],
                    choices=json_response['choices'],
                    id=json_response['id'],
                    created=json_response['created'],
                    model=json_response['model'],
                    usage=json_response['usage']
                )

            else:
                # Handle non-event-stream responses here if necessary
                response_data = response.json()
                modelResponse = litellm.ModelResponse(response_data)

        except Exception as e:
            # Catch any exceptions and store the error message
            print(e)
            response_data = {"error": str(e)}
            modelResponse = litellm.ModelResponse(
                object="error",
                error=response_data["error"]
            )

        return modelResponse

    def generate_unique_id(self):
        """
        Generates a unique identifier (ID) for a new object or request.

        This method generates a unique string ID, typically used for identifying 
        individual requests, records, or objects in a system. The ID is designed 
        to be globally unique and can be used to track or differentiate between 
        multiple instances or operations.

        Returns:
            str: A unique identifier as a string, usually formatted as a UUID or 
                a similarly unique string.
        """
        # You can customize this as needed for generating unique IDs
        return str(int(time.time() * 1000))

    def streaming(self, *args, **kwargs) -> Iterator[GenericStreamingChunk]:
            raise SnowflakeCortexCustomServiceError(status_code=500, message="Not implemented yet!")

    async def acompletion(self, *args, **kwargs) -> ModelResponse:
            raise SnowflakeCortexCustomServiceError(status_code=500, message="Not implemented yet!")

    async def astreaming(self, *args, **kwargs) -> AsyncIterator[GenericStreamingChunk]:
            raise SnowflakeCortexCustomServiceError(status_code=500, message="Not implemented yet!")


