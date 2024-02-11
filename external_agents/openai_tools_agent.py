from typing import Any, Optional, List

from pydantic import PrivateAttr

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from crewai.agents.agent_interface import AgentWrapperParent


class OpenAIToolsAgent(AgentWrapperParent):
    _llm: ChatOpenAI = PrivateAttr()
    _prompt: ChatPromptTemplate = PrivateAttr()
    _tools: List[Any] = PrivateAttr(default=[])
    _role: str = PrivateAttr(default="")
    _allow_delegation: bool = PrivateAttr(default=False)
    _agent_executor: Any = PrivateAttr(default=None)

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
        self._llm = llm
        self._prompt = prompt
        self._role = role
        self._allow_delegation = allow_delegation
        self.init(tools)

    def execute_task(
        self,
        task: str,
        context: Optional[str] = None,
        tools: Optional[List[Any]] = None,
    ) -> str:
        # Most agents require their tools list to be known at creation time,
        # so might need to re-create the agent if there are new tools added
        # TODO: compare whether they're actually the same tools!
        if tools is not None and len(tools) != len(self._tools):
            self.init(tools)

        # TODO: better wrap the context as a sequence of messages
        return self._agent_executor.invoke(
            {"input": task, "chat_history": [HumanMessage(content=context)]}
        )["output"]

    def init(self, tools: List[Any]) -> None:
        self._tools = tools
        agent = create_openai_tools_agent(self._llm, tools, self._prompt)

        # Create an agent executor by passing in the agent and tools
        self._agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    @property
    def allow_delegation(self) -> bool:
        return self._allow_delegation

    @property
    def role(self) -> str:
        return self._role

    @property
    def tools(self) -> List[Any]:
        return self._tools
