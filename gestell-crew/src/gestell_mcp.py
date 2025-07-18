from os import getenv
from dotenv import load_dotenv
from mcp import StdioServerParameters

load_dotenv()

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@gestell/mcp@latest"],
    env={"GESTELL_API_KEY": getenv("GESTELL_API_KEY")},
)
