from typing import Any, Optional, List

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from crewai.agents.agent_interface import AgentWrapperParent


class OpenAIToolsAgent(AgentWrapperParent):

    def __init__(
        self,
        llm: ChatOpenAI,
        prompt: ChatPromptTemplate,
        tools: List[Any],
        role: str,
        allow_delegation: bool = False,
        **data: Any
    ):
        super().__init__(**data)
        self.data["llm"] = llm
        self.data["prompt"] = prompt
        self.data["role"] = role
        self.data["allow_delegation"] = allow_delegation
        self.init_tools(tools)

    def execute_task(
        self,
        task: str,
        context: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None,
    ) -> str:
        # Most agents require their tools list to be known at creation time,
        # so might need to re-create the agent if there are new tools added
        # TODO: also compare whether they're actually the same tools!
        if tools is not None and len(tools) != len(self._tools):
            self.init_tools(tools)

        if context:
            context = [AIMessage(content=ctx) for ctx in context]
        else:
            context = []

        return self.data["agent_executor"].invoke(
            {"input": task, "chat_history": context}
        )["output"]

    def init_tools(self, tools: List[Any]) -> None:
        self.data["tools"] = tools
        agent = create_openai_tools_agent(self.data["llm"], tools, self.data["prompt"])

        # Create an agent executor by passing in the agent and tools
        self.data["agent_executor"] = AgentExecutor(
            agent=agent, tools=tools, verbose=True
        )

    @property
    def allow_delegation(self) -> bool:
        return self.data["allow_delegation"]

    @property
    def role(self) -> str:
        return self.data["role"]

    @property
    def tools(self) -> List[Any]:
        return self.data["tools"]
