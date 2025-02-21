import os
from dotenv import load_dotenv
from crewai import LLM


def load_bedrock_llm() -> LLM:
    """
    Initializes and configures a Bedrock LLM (Claude-3) instance for use with CrewAI.

    This function:
    1. Loads environment variables from .env file
    2. Configures the Bedrock LLM with Claude-3 Sonnet model
    3. Returns a CrewAI-compatible LLM instance

    Required environment variables:
    - AWS credentials should be configured in the environment or ~/.aws/credentials
    - Region settings should be configured in AWS CLI or environment

    Returns:
        LLM: Configured CrewAI LLM instance using Claude-3 Sonnet model

    Example:
        llm = load_bedrock_llm()
        response = llm.generate("Your prompt here")

    Notes:
        - Uses Claude-3 Sonnet model (2024-02-29 version)
        - Ensure AWS Bedrock access is properly configured
        - Make sure AWS IAM permissions include Bedrock model access
    """
    # Load environment variables from .env file
    # This step is crucial for AWS configuration if not using AWS CLI
    load_dotenv()

    # Initialize and configure the Bedrock LLM with Claude-3 Sonnet model
    # Using CrewAI's LLM wrapper for compatibility
    bedrock_llm = LLM(
        model=os.getenv("BEDROCK_MODEL_ID")
    )

    return bedrock_llm
