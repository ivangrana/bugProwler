from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

# Setup your database
db = SqliteDb(db_file="tmp/agno.db")

system_message = """You are a reconnaissance agent. Your goal is to gather information about a target system.
You should provide detailed explanations of each found assets and provide possible attack vectors."""

# Configure the MCP tool connection
mcp_tools = MCPTools(
    url="http://0.0.0.0:8080/mcp",
    refresh_connection=True,  # Enable automatic reconnection
)

recon_agent = Agent(
    name="reconProwler",
    model=OpenAIChat(id="gpt-4.1-nano"),
    db=db,
    add_history_to_context=True,
    num_history_runs=5,
    description="Bug Bounty Recon Agent",
    instructions=system_message,
    markdown=True,
    reasoning=False,
    debug_level=1,
    tools=[mcp_tools],
)
