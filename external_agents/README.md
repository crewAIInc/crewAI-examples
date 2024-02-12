# Adding external agents to the crew

This example shows how you can add external agents to the crew, on the example of a langchain agent.

You do this by inheriting from the `AgentWrapperParent` class and implementing its abstract methods.

These agents can then be mixed and matched with native CrewAI agents.

An implementation for langchain agent is already provided and can be used as in the following example:

    ```python
    from langchain import hub
    from langchain.agents import create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    from langchain_community.tools import DuckDuckGoSearchRun
    
    from crewai.agents.langchain_agent import LangchainAgent
    
    llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
    tools = [DuckDuckGoSearchRun()]    
    researcher_prompt = hub.pull("hwchase17/openai-tools-agent")

    researcher_agent = AgentExecutor(
        agent=create_openai_tools_agent(llm, tools, researcher_prompt),
        tools=tools,
        verbose=True,
    )
    
    researcher = LangchainAgent(
        agent=researcher_agent,
        tools=[search_tool],
        role="Senior Research Analyst",
        allow_delegation=False,
    )

You need to pass a function that creates the desired agent from the list of its tools, to enable adding other agents as tools at runtime (for delegation).
