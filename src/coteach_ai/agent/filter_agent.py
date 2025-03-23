from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from ..core import Prompts, settings
from ..errors import DataError
from .agent import Agent
from .config.ai_config import agent_config
from .config.constants import State


class FilterAgent(Agent):
	def __init__(self, agent_id: str) -> None:
		super().__init__(agent_id)
		if not agent_config.llm or not agent_config.search_tool:
			msg = "AIModel must be initialized with an LLM and search tool before creating FilterAgent"
			raise DataError(message=msg, status=422)
		self.filter_agent = create_react_agent(
			name="filter_agent",
			debug=settings.app.DEBUG,
			model=agent_config.llm,
			tools=[agent_config.search_tool],
			prompt=Prompts.RESEARCH_PROMPT,
		)

	async def execute(self, input_data: State) -> dict[str, Any]:
		if "research_summary" not in input_data or not input_data["research_summary"]:
			msg = "input_data must contain 'research_summary' from ResearchAgent"
			raise DataError(message=msg, status=422)

		result = await self.filter_agent.ainvoke(
			{
				"messages": [
					HumanMessage(content=input_data.get("research_summary", "")),  # type:ignore
				],
			},
		)
		filtered_modules = result["messages"][-1].content

		return {"filtered_modules": filtered_modules}


filter_agent = FilterAgent("filter_agent")
