#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import os

from exam_prep.crew import ExamPrep

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_user_input():
    """
    Get exam information from the user through command line input.
    """
    print("\nWelcome to the AI Study Planning Assistant!")
    print("Please provide your exam information in natural language.")
    print("Example: 'I have a test on statistics in 4 days. Topics are probability, distributions, and hypothesis testing.'")
    print("\nEnter your exam information (press Enter twice to finish):")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines:  # If empty line and we have some input
            break
        if line:  # If line is not empty
            lines.append(line)
    
    return " ".join(lines)

def run():
    """
    Runs the agentic study assistant with user input and saves output to markdown.
    """
    try:
        # Get input from user
        student_input = get_user_input()
        
        # Create inputs dictionary
        inputs = {
            "student_input": student_input
        }

        # Run the crew with user input
        result = ExamPrep().crew().kickoff(inputs=inputs)
        
        # Create output directory if it doesn't exist
        if not os.path.exists("output"):
            os.makedirs("output")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"study_plan_{timestamp}.md"
        
        # Save the output to markdown file
        with open(f"output/{filename}", "w", encoding="utf-8") as f:
            f.write(str(result))
        
        print(f"\nStudy plan has been saved to: output/{filename}")
        
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()