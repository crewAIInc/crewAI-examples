from typing import Optional

from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

from self_evaluation_loop_flow.crews.shakespeare_crew.shakespeare_crew import (
    ShakespeareanXPostCrew,
)
from self_evaluation_loop_flow.crews.x_post_review_crew.x_post_review_crew import (
    XPostReviewCrew,
)


class ShakespeareXPostFlowState(BaseModel):
    x_post: str = ""
    feedback: Optional[str] = None
    valid: bool = False
    retry_count: int = 0


class ShakespeareXPostFlow(Flow[ShakespeareXPostFlowState]):

    @start("retry")
    def generate_shakespeare_x_post(self):
        print("Generating Shakespearean X post")
        topic = "Flying cars"
        result = (
            ShakespeareanXPostCrew()
            .crew()
            .kickoff(inputs={"topic": topic, "feedback": self.state.feedback})
        )

        print("X post generated", result.raw)
        self.state.x_post = result.raw

    @router(generate_shakespeare_x_post)
    def evaluate_x_post(self):
        if self.state.retry_count > 3:
            return "max_retry_exceeded"

        result = XPostReviewCrew().crew().kickoff(inputs={"x_post": self.state.x_post})
        self.state.valid = result["valid"]
        self.state.feedback = result["feedback"]

        print("valid", self.state.valid)
        print("feedback", self.state.feedback)
        self.state.retry_count += 1

        if self.state.valid:
            return "complete"

        return "retry"

    @listen("complete")
    def save_result(self):
        print("X post is valid")
        print("X post:", self.state.x_post)

        # Save the valid X post to a file
        with open("x_post.txt", "w") as file:
            file.write(self.state.x_post)

    @listen("max_retry_exceeded")
    def max_retry_exceeded_exit(self):
        print("Max retry count exceeded")
        print("X post:", self.state.x_post)
        print("Feedback:", self.state.feedback)


def kickoff():
    shakespeare_flow = ShakespeareXPostFlow()
    shakespeare_flow.kickoff()


def plot():
    shakespeare_flow = ShakespeareXPostFlow()
    shakespeare_flow.plot()


if __name__ == "__main__":
    kickoff()
