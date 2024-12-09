# Run as `python src/marketing_posts/test.py`

from litellm import completion
import os
import dotenv

# Replace with your own .env file
dotenv.load_dotenv("/Users/apgupta/git/crewAI-examples/marketing_strategy/.env")

## set ENV variables
# os.environ["AZURE_API_KEY"] = ""
# os.environ["AZURE_API_BASE"] = ""
# os.environ["AZURE_API_VERSION"] = ""

# azure call
response = completion(
    model = "azure/sfc-cortex-analyst-dev",
    messages = [{ "content": "Hello, how are you?","role": "user"}]
)
print (response)