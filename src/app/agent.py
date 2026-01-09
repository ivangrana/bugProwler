from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from agno.os import AgentOS

agno_assist = Agent(
    name="Agno Assist",
    model=Ollama(id="llama3.2:1b"),
    description="You help answer math questions.",
    instructions="Answer using math proofs. and formulas. Provide step-by-step explanations.",
    markdown=True,
    reasoning=True,
    debug_level=2,
)

play = AgentOS(agents=[agno_assist])
app = play.get_app()

if __name__ == "__main__":
    # play.serve("main:app", reload=True)
    agno_assist.print_response(
        "proof of the derivative of sin(x)",
        stream=True,
        show_full_reasoning=True,
        debug_mode=True,
    )
