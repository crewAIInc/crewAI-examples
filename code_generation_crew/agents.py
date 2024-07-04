from crewai_tools.tools import CodeInterpreterTool

from crewai import Agent

code_interpreter_tool = CodeInterpreterTool()


class Agents:
    def quant_financial_agent(self):
        return Agent(
            role="Quant Financial Engineer",
            goal="Analyze the provided information and if needed write code and run it to generate insights.",
            backstory="Expert in analyzing company cultures and identifying key values and needs from various sources, including websites and brief descriptions.",
            verbose=True,
            allow_code_execution=True,
            allow_delegation=False,
        )

    def reporting_analyst(self):
        return Agent(
            role="Reporting Analyst",
            goal="Create detailed reports based on the topic provided data analysis and research findings",
            tools=[],
            backstory="""You're a meticulous analyst with a keen eye for detail. You're known for
    					your ability to turn complex data into clear and concise reports, making
    					it easy for others to understand and act on the information you provide.""",
            verbose=True,
        )
