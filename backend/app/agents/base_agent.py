import os
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

class BaseAgent:
    """
    Base class for all agents.
    """
    def __init__(self, tools: List[BaseTool], model: str = "gpt-4o-mini"):
        self.tools = tools
        self.llm = ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"))

    def invoke_tool(self, tool_name: str, tool_input: Any) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.invoke(tool_input)
        raise ValueError(f"Tool {tool_name} not found")

    async def ainvoke_tool(self, tool_name: str, tool_input: Any) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                return await tool.ainvoke(tool_input)
        raise ValueError(f"Tool {tool_name} not found")

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the process method")