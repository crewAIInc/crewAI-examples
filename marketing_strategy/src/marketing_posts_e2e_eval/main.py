#!/usr/bin/env python
import asyncio
import sys
from dotenv import load_dotenv
from marketing_posts_e2e_eval.marketing_crew.marketing_crew import MarketingPostsCrew
from marketing_posts_e2e_eval.evaluator_crew.eval_crew import EvaluatorCrew
from snowflake.snowpark.session import Session
from trulens.connectors.snowflake import SnowflakeConnector
from trulens.core import Feedback
from trulens.core.schema.feedback import FeedbackResult

from typing import Optional, Dict

from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

load_dotenv()

def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'customer_domain': 'crewai.com',
        'previous_marketing_post': None,
        'feedback': None,
        'project_description': """
CrewAI, a leading provider of multi-agent systems, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase CrewAI's advanced AI-driven solutions, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of CrewAI's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of CrewAI's services among enterprise clients.
""",
    }
    MarketingPostsCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'customer_domain': 'crewai.com',
        'project_description': """
CrewAI, a leading provider of multi-agent systems, aims to revolutionize marketing automation for its enterprise clients. This project involves developing an innovative marketing strategy to showcase CrewAI's advanced AI-driven solutions, emphasizing ease of use, scalability, and integration capabilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of CrewAI's platform.

Customer Domain: AI and Automation Solutions
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of CrewAI's services among enterprise clients.
"""
    }
    try:
        MarketingPostsCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

class MarketingPostFlowState(BaseModel):
    marketing_post: str = ""
    feedback: Optional[str] = None
    quality: int = 0
    retry_count: int = 0


class MarketingPostFlow(Flow[MarketingPostFlowState]):

    def __init__(self, inputs: dict[str, str]):
        super().__init__()
        self._flow_inputs = inputs

    @start("retry")
    def generate_marketing_post(self):
        print("Generating Marketing post")
        inputs = {
            'customer_domain': self._flow_inputs['customer_domain'],
            'project_description': self._flow_inputs['project_description'],
            'previous_marketing_post': self.state.marketing_post,
            'feedback': self.state.feedback,
        }
        result = MarketingPostsCrew().crew().kickoff(inputs=inputs)

        print("Marketing post generated", result.raw)
        self.state.marketing_post = result.raw

    @router(generate_marketing_post)
    def evaluate_marketing_post(self):
        if self.state.retry_count > 3:
            return "max_retry_exceeded"

        result = EvaluatorCrew().crew().kickoff(inputs={"marketing_post": self.state.marketing_post})
        self.state.quality = result["quality"]
        self.state.feedback = result["feedback"]

        print("quality", self.state.quality)
        print("feedback", self.state.feedback)
        self.state.retry_count += 1

        tru_snowflake_connector.add_feedback(
            FeedbackResult(
                record_id=str(round(time.time() * 1000)),
                name=f"{self.inputs['customer_domain']}_quality_score",
                result=self.state.quality,
                feedback_definition_id=fid,
            )
        )

        if self.state.quality > 3:
            return "complete"

        return "retry"

    @listen("complete")
    def save_result(self):
        print("Marketing strategy results are valid")
        print("Results:", self.state.marketing_post)

        with open("results.txt", "w") as file:
            file.write(self.state.marketing_post)

    @listen("max_retry_exceeded")
    def max_retry_exceeded_exit(self):
        print("Max retry count exceeded")
        print("Results:", self.state.marketing_post)
        print("Feedback:", self.state.feedback)

connection_params = {
    "account":  "SFENGINEERING-MLPLATFORMTEST",
    "user": "",
    "password": "",
    "database": "CYIN",
    "schema": "MODEL_MONITOR_SCHEMA",
    "warehouse": "CYIN",
}

snowpark_session = Session.builder.configs(connection_params).create()
tru_snowflake_connector = SnowflakeConnector(snowpark_session=snowpark_session)
fid = tru_snowflake_connector.add_feedback_definition(Feedback(lambda x: x, name="quality_score"))

def kickoff(inputs: Optional[Dict[str, str]] = None):
    if not inputs:
        inputs = {
            'customer_domain': 'crewai.com',
            'project_description': """
            CrewAI, a leading provider of multi-agent systems, aims to revolutionize marketing automation for its enterprise clients.
            This project involves developing an innovative marketing strategy to showcase CrewAI's advanced AI-driven solutions,
            emphasizing ease of use, scalability, and integration capabilities.
            The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of CrewAI's platform.

            Customer Domain: AI and Automation Solutions
            Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of CrewAI's services among enterprise clients.
            Secondary goal: During the execution of the multi-agent system/tasks, evaluate the quality of answers at each step.
            """,
        }
    asyncio.run(MarketingPostFlow(inputs=inputs).kickoff())
