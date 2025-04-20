
import asyncio
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from .tools.base import Tool
from .utils.connections import setup_mcp_connections
from .utils.history_util import MessageHistory
from .utils.tool_util import execute_tools

@dataclass
class ModelConfig:
    """Configuration settings for model parameters."""

    model: str = "'qwen-plus"
    max_tokens: int = 4096
    temperature: float = 1.0
    context_window_tokens: int = 180000

class Agent:
    def __init__(
        self,
        name: str, 
        system: str,
        tools: list[Tool] | None = None,
        mcp_servers: list[dict[str, Any]] | None = None,
        config: ModelConfig | None = None,
        verbose: bool = False,
        client: OpenAI | None = None,
        ):
        self.name = name
        self.system = system
        self.verbose = verbose
        self.tools = list(tools or [])
        self.config = config or ModelConfig()
        self.mcp_servers = mcp_servers or []
        self.client = client or OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),  
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        self.history = MessageHistory(
            model=self.config.model,
            system=self.system,
            context_window_tokens=self.config.context_window_tokens,
            client=self.client,
        )

        if self.verbose:
            print(f"\n[{self.name}] Agent initialized")

    def _prepare_api_params(self) -> dict[str, Any]:
        """Prepare parameters for OPENAI API call."""
        # Use system prompt directly without prefixing
        return {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            # "system": self.system,
            "messages": self.history.format_for_api(),
            "tools": [tool.to_dict() for tool in self.tools],
        }
    
    async def _agent_loop(self, user_input: str) -> list[dict[str, Any]]:
        """Process user input and handle tool calls in a loop"""
        if self.verbose:
            print(f"\n[{self.name}] Received: {user_input}")
        await self.history.add_message("user", user_input, None)

        tool_dict = {tool.name: tool for tool in self.tools}

        while True:
            self.history.truncate()
            params = self._prepare_api_params()

            completion = self.client.chat.completions.create(**params)
            
            output = completion.model_dump()
            response = output["choices"][0]["message"]
            if  response['content'] is None:
                response['content'] = ""

            print(response)
            tool_calls = response["tool_calls"]

            # 如果不需要调用工具，则直接返回最终答案
            if response['tool_calls'] == None:  # 如果模型判断无需调用工具，则将assistant的回复直接打印出来，无需进行模型的第二轮调用
                print(f"无需调用工具，我可以直接回复：{response['content']}")
                return

            # if self.verbose:
            #     for block in response.content:
            #         if block.type == "text":
            #             print(f"\n[{self.name}] Output: {block.text}")
            #         elif block.type == "tool_use":
            #             params_str = ", ".join(
            #                 [f"{k}={v}" for k, v in block.input.items()]
            #             )
            #             print(
            #                 f"\n[{self.name}] Tool call: "
            #                 f"{block.name}({params_str})"
            #             )

            # await self.history.add_message(
            #     "assistant", response.content, response.usage
            # )

            if tool_calls is not None:
                print(tool_calls)
                tool_results = await execute_tools(
                    tool_calls,
                    tool_dict,
                )
                if self.verbose:
                    for block in tool_results:
                        print(
                            f"\n[{self.name}] Tool result: "
                            f"{block.get('content')}"
                        )
                await self.history.add_message("user", tool_results)
            else:
                return response

    async def run_async(self, user_input: str) -> list[dict[str, Any]]:
        """Run agent with MCP tools asynchronously."""
        async with AsyncExitStack() as stack:
            original_tools = list(self.tools)

            try:
                mcp_tools = await setup_mcp_connections(
                    self.mcp_servers, stack
                )
                self.tools.extend(mcp_tools)
                return await self._agent_loop(user_input)
            finally:
                self.tools = original_tools

    def run(self, user_input: str) -> list[dict[str, Any]]:
        """Run agent synchronously"""
        return asyncio.run(self.run_async(user_input))