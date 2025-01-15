# Author: Sean Iannuzzi
# Created: January 10, 2024
# Updated: January 13, 2024
# Notes:
# - Changed payload to be a parameter
# - Change the name to a more descriptive name and format
# - Removed error handling class and made a separate file

import litellm
from litellm import CustomLLM
from litellm.types.utils import GenericStreamingChunk, ModelResponse
import requests
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator
from snowflake_cortex_service_custom_error import SnowflakeCortexCustomServiceError
from snowflake_auth_jwt_generator import JWTGenerator

"""
Snowflake Cortext Service Custom LLM for Snowflake Cortex LLM Integration
This Snowflake Cortext Custom LLM Class enables integration with Snowflake Cortex through their API endpoints. 
The implementation provides a flexible interface to connect to the Snowflake API, manage API requests, 
and handle the necessary configurations for completing language model tasks. 

Note: 
You could change this to inheret from BaseLLM instead of CustomLLM if you want to use the base class
for a more generic implementation.
"""
class SnowflakeCortexCustomServiceLLM(CustomLLM):
    """
    SnowflakeCortexCustomServiceLLM: A custom implementation of a Snowflake Cortext Service (LLM) 
    designed to integrate with the Snowflake API and be registered as a provider
    within LiteLLM and Crew AI agents.

    This class extends the base `CustomLLM` class to facilitate the integration of a custom language 
    model that interacts with the Snowflake Cortext Service API. By defining a `custom_provider_map`, 
    this custom model can be invoked within Crew AI agents for specific tasks, leveraging flexible 
    configuration options such as `base_url`, `api_key`, and other model parameters. 

    The primary purpose of this Snowflake Cortext Service Custom LLM is to enable communication 
    with the Snowflake Cortext Service API, allowing the model to interact with Snowflake data,
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

        # Create an LLM instance using the custom Snowflake Cortext Service LLM
        custom_llm = LLM(
            model="snowflake-cortex-custom-service-llm/snowflake-cortex-custom-service-llm",
            api_base = os.environ.get("SNOWFLAKE_CORTEXT_CUSTOM_LLM_BASE_URL"),
            api_key = os.environ.get("SNOWFLAKE_CUSTOMLLM_PRIVATE_KEY"),
        )

        # Use the custom LLM to generate a response
        response = snowflakecortex_custom_llm.completion(messages=[{"role": "user", "content": "Show me information about cases"}])

        # Use the liteLLM to generate a response
        response = custom_llm.call(messages=[{"role": "user", "content": "Show me information about cases"}])

    The SnowflakeCortexCustomServiceLLM class is designed to integrate tightly with the Snowflake Cortex ServiceAPI, 
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
        Handles the completion request for the custom language model.

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
                messages = kwargs.get("messages", [])
                prompt_content = " ".join([msg["content"] for msg in messages])
                self.snowflakePromptTemplate["query"] = prompt_content
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

            # Make the POST request to the API
            response = requests.post(server_url, headers=headers, json=payload)
            response_data = response.json()

            # Flatten the response data
            flat_data = self.flatten_json(response_data)

            # Convert the flattened data to a string, formatting each key-value pair
            flat_string = ', '.join([f"{key}={value}" for key, value in flat_data.items()])

            #this helps the agent know that this is the final answer
            #you can add in some additional logic to customize this
            flat_string = "Final Answer: " + flat_string

            prompt_tokens = self.count_tokens(prompt_content)
            completion_tokens = self.count_tokens(flat_string)
            total_tokens = prompt_tokens + completion_tokens

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
                            "content": flat_string,
                            "role": "assistant"
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            }

            # Creating a new ModelResponse instance using the JSON data
            modelResponse = litellm.ModelResponse(
                object=json_response['object'],
                choices=json_response['choices'],
                id=json_response['id'],
                created=json_response['created'],
                model=json_response['model'],
                usage=json_response['usage']
            )

        except Exception as e:
            # Catch any exceptions and store the error message
            print(e)
            response_data = {"error": str(e)}
            modelResponse = litellm.ModelResponse(
                object="error",
                error=response_data["error"]
        )

        return modelResponse

    def count_tokens(self, text):
        """
        Counts the number of tokens in a given text input.

        This method takes a string of text as input and calculates the number of tokens 
        based on the tokenization process used by the custom language model. The token count 
        is important for determining the model's resource usage, such as prompt length 
        and completion limits.

        Parameters:
            text (str): The input text whose tokens need to be counted.

        Returns:
            int: The number of tokens in the input text.
        """
        """Estimate tokens by counting words."""
        return len(text.split())
    
    def flatten_json(self, nested_json, parent_key='', sep='_'):
        """
        Flattens a nested JSON object into a single-level dictionary.

        This method recursively flattens a JSON object (which may contain nested dictionaries 
        or lists) into a flat dictionary, where nested keys are combined with the parent key 
        separated by a specified separator. This is useful for transforming complex nested data 
        structures into simpler, flat formats for easier processing or storage.

        Parameters:
            nested_json (dict or list): The JSON object to be flattened, which may be a 
                                        dictionary or list with nested structures.
            parent_key (str, optional): The base key to prefix to the flattened keys. 
                                        Defaults to an empty string.
            sep (str, optional): The separator to use between parent and child keys. 
                                Defaults to an underscore ('_').

        Returns:
            dict: A flattened version of the input JSON object with keys as concatenated 
                parent-child key names.
        """
       
        items = []
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_json(v, new_key, sep=sep).items())  # Recursive call to flatten nested dictionaries
            else:
                items.append((new_key, v))  # Add key-value pair to the flat list
        return dict(items)

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
