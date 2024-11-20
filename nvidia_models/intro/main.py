import logging
import os
from typing import Any, Dict, List, Optional, Union

import litellm
from crewai import LLM, Agent, Crew, Process, Task
from crewai.utilities.exceptions.context_window_exceeding_exception import (
    LLMContextLengthExceededException,
)
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()


class nvllm(LLM):
    def __init__(
        self,
        llm: ChatNVIDIA,
        model_str: str,
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
        callbacks: List[Any] = None,
        **kwargs,
    ):
        self.model = model_str
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
        self.kwargs = kwargs
        self.llm = llm

        if callbacks is None:
            self.callbacks = callbacks = []

        self.set_callbacks(callbacks)

    def call(self, messages: List[Dict[str, str]], callbacks: List[Any] = None) -> str:
        if callbacks is None:
            callbacks = []
        if callbacks and len(callbacks) > 0:
            self.set_callbacks(callbacks)

        try:
            params = {
                "model": self.llm.model,
                "input": messages,
                "timeout": self.timeout,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "n": self.n,
                "stop": self.stop,
                "max_tokens": self.max_tokens or self.max_completion_tokens,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
                "logit_bias": self.logit_bias,
                "response_format": self.response_format,
                "seed": self.seed,
                "logprobs": self.logprobs,
                "top_logprobs": self.top_logprobs,
                "api_key": self.api_key,
                **self.kwargs,
            }

            response = self.llm.invoke(**params)
            return response.content
        except Exception as e:
            if not LLMContextLengthExceededException(str(e))._is_context_limit_error(
                str(e)
            ):
                logging.error(f"LiteLLM call failed: {str(e)}")

            raise  # Re-raise the exception after logging

    def set_callbacks(self, callbacks: List[Any]):
        callback_types = [type(callback) for callback in callbacks]
        for callback in litellm.success_callback[:]:
            if type(callback) in callback_types:
                litellm.success_callback.remove(callback)

        for callback in litellm._async_success_callback[:]:
            if type(callback) in callback_types:
                litellm._async_success_callback.remove(callback)

        litellm.callbacks = callbacks


model = os.environ.get("MODEL", "meta/llama-3.1-8b-instruct")
llm = ChatNVIDIA(model=model)
default_llm = nvllm(model_str="nvidia_nim/" + model, llm=llm)

os.environ["NVIDIA_NIM_API_KEY"] = os.environ.get("NVIDIA_API_KEY")

# Create a researcher agent
researcher = Agent(
    role="Senior Researcher",
    goal="Discover groundbreaking technologies",
    verbose=True,
    llm=default_llm,
    backstory=(
        "A curious mind fascinated by cutting-edge innovation and the potential "
        "to change the world, you know everything about tech."
    ),
)

# Task for the researcher
research_task = Task(
    description="Identify the next big trend in AI",
    agent=researcher,  # Assigning the task to the researcher
    expected_output="Data Insights",
)


# Instantiate your crew
tech_crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    process=Process.sequential,  # Tasks will be executed one after the other
)

# Begin the task execution
tech_crew.kickoff()
