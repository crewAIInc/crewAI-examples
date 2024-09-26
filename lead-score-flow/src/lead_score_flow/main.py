#!/usr/bin/env python
import asyncio
from typing import List

from crewai.flow.flow import Flow, listen, or_, router, start
from pydantic import BaseModel

from lead_score_flow.constants import JOB_DESCRIPTION
from lead_score_flow.crews.lead_response_crew.lead_response_crew import LeadResponseCrew
from lead_score_flow.crews.lead_score_crew.lead_score_crew import LeadScoreCrew
from lead_score_flow.types import Candidate, CandidateScore, ScoredCandidate
from lead_score_flow.utils.candidateUtils import combine_candidates_with_scores


class LeadScoreState(BaseModel):
    candidates: List[Candidate] = []
    candidate_score: List[CandidateScore] = []
    hydrated_candidates: List[ScoredCandidate] = []
    scored_leads_feedback: str = ""


class EmailAutoResponderFlow(Flow[LeadScoreState]):
    initial_state = LeadScoreState

    @start()
    def load_leads(self):
        import csv
        from pathlib import Path

        # Get the path to leads.csv in the same directory
        current_dir = Path(__file__).parent
        csv_file = current_dir / "leads.csv"

        candidates = []
        with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create a Candidate object for each row
                print("Row:", row)
                candidate = Candidate(**row)
                candidates.append(candidate)

        # Update the state with the loaded candidates
        self.state.candidates = candidates

    @listen(or_(load_leads, "scored_leads_feedback"))
    async def score_leads(self):
        print("Scoring leads")
        tasks = []

        async def score_single_candidate(candidate: Candidate):
            result = await (
                LeadScoreCrew()
                .crew()
                .kickoff_async(
                    inputs={
                        "candidate_id": candidate.id,
                        "name": candidate.name,
                        "bio": candidate.bio,
                        "job_description": JOB_DESCRIPTION,
                        "additional_instructions": self.state.scored_leads_feedback,
                    }
                )
            )

            self.state.candidate_score.append(result.pydantic)

        for candidate in self.state.candidates:
            print("Scoring candidate:", candidate.name)
            task = asyncio.create_task(score_single_candidate(candidate))
            tasks.append(task)

        candidate_scores = await asyncio.gather(*tasks)
        print("Finished scoring leads: ", len(candidate_scores))

    @router(score_leads)
    def human_in_the_loop(self):
        print("Finding the top 3 candidates for human to review")

        # Combine candidates with their scores using the helper function
        self.state.hydrated_candidates = combine_candidates_with_scores(
            self.state.candidates, self.state.candidate_score
        )

        # Sort the scored candidates by their score in descending order
        sorted_candidates = sorted(
            self.state.hydrated_candidates, key=lambda c: c.score, reverse=True
        )
        self.state.hydrated_candidates = sorted_candidates

        # Select the top 3 candidates
        top_candidates = sorted_candidates[:3]

        print("Here are the top 3 candidates:")
        for candidate in top_candidates:
            print(
                f"ID: {candidate.id}, Name: {candidate.name}, Score: {candidate.score}, Reason: {candidate.reason}"
            )

        # Present options to the user
        print("\nPlease choose an option:")
        print("1. Quit")
        print("2. Redo lead scoring with additional feedback")
        print("3. Proceed with writing emails to all leads")

        choice = input("Enter the number of your choice: ")

        if choice == "1":
            print("Exiting the program.")
            exit()
        elif choice == "2":
            feedback = input(
                "\nPlease provide additional feedback on what you're looking for in candidates:\n"
            )
            self.state.scored_leads_feedback = feedback
            print("\nRe-running lead scoring with your feedback...")
            return "scored_leads_feedback"
        elif choice == "3":
            print("\nProceeding to write emails to all leads.")
            return "generate_emails"
        else:
            print("\nInvalid choice. Please try again.")
            return "human_in_the_loop"

    @listen("generate_emails")
    async def write_and_save_emails(self):
        import re
        from pathlib import Path

        print("Writing and saving emails for all leads.")

        # Determine the top 3 candidates to proceed with
        top_candidate_ids = {
            candidate.id for candidate in self.state.hydrated_candidates[:3]
        }

        tasks = []

        # Create the directory 'email_responses' if it doesn't exist
        output_dir = Path(__file__).parent / "email_responses"
        print("output_dir:", output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        async def write_email(candidate):
            # Check if the candidate is among the top 3
            proceed_with_candidate = candidate.id in top_candidate_ids

            # Kick off the LeadResponseCrew for each candidate
            result = await (
                LeadResponseCrew()
                .crew()
                .kickoff_async(
                    inputs={
                        "candidate_id": candidate.id,
                        "name": candidate.name,
                        "bio": candidate.bio,
                        "proceed_with_candidate": proceed_with_candidate,
                    }
                )
            )

            # Sanitize the candidate's name to create a valid filename
            safe_name = re.sub(r"[^a-zA-Z0-9_\- ]", "", candidate.name)
            filename = f"{safe_name}.txt"
            print("Filename:", filename)

            # Write the email content to a text file
            file_path = output_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.raw)

            # Return a message indicating the email was saved
            return f"Email saved for {candidate.name} as {filename}"

        # Create tasks for all candidates
        for candidate in self.state.hydrated_candidates:
            task = asyncio.create_task(write_email(candidate))
            tasks.append(task)

        # Run all email-writing tasks concurrently and collect results
        email_results = await asyncio.gather(*tasks)

        # After all emails have been generated and saved
        print("\nAll emails have been written and saved to 'email_responses' folder.")
        for message in email_results:
            print(message)


async def run():
    """
    Run the flow.
    """
    email_auto_response_flow = EmailAutoResponderFlow()
    await email_auto_response_flow.kickoff()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
