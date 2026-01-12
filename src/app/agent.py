from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS

# Setup your database
db = SqliteDb(db_file="agno.db")

system_message = """You are an API pentesting agent. Your goal is to identify vulnerabilities in APIs
and report them to the developer. You should provide detailed explanations of the vulnerabilities and suggest fixes."""

agno_assist = Agent(
    name="Agno Assist",
    model=OpenAIChat(id="gpt-4.1-nano"),
    db=db,
    add_history_to_context=True,
    num_history_runs=5,
    description="Bug Bounty Hunter Agent",
    instructions=system_message,
    markdown=True,
    reasoning=False,
    debug_level=1,
)

play = AgentOS(agents=[agno_assist])
app = play.get_app()
