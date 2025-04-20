import os
import sys
import nest_asyncio
nest_asyncio.apply()

parent_dir = os.path.dirname(os.getcwd())
sys.path.insert(0, parent_dir)
from agents.agent import Agent, ModelConfig
from agents.tools.think import ThinkTool

# Standard Python tool
think_tool = ThinkTool()

# Python MCP server
calculator_server_path = os.path.abspath(os.path.join(os.getcwd(), "agents/tools/calculator_mcp.py"))
calculator_server = {
    "type": "stdio",
    "command": "python",
    "args": [calculator_server_path]
}
print(f"Calculator server configured: {'Yes' if calculator_server else 'No'}")

# Create agent config 
system_prompt = """
You are a helpful assistant with access to:
1. Web search (brave_web_search, brave_local_search)
2. Mathematical calculator (calculate) 
3. A tool to think and reason (think)

Always use the most appropriate tool for each task.
"""


# Initialize agent with standard tools and MCP servers
agent = Agent(
    name="Multi-Tool Agent",
    system=system_prompt,
    tools=[think_tool], 
    mcp_servers=[calculator_server], 
    config=ModelConfig(
        model="qwen-plus", 
        max_tokens=4096,
        temperature=1.0
    ),
    verbose=True
)

def test_agent():
    agent.run("What's the square root of the OKC population in 2022")