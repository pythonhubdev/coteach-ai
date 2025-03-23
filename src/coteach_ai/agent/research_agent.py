from typing import Any

from langgraph.prebuilt import create_react_agent

from ..core import Prompts, settings
from ..errors import DataError
from .agent import Agent
from .config.ai_config import agent_config
from .config.constants import State


class ResearchAgent(Agent):
	"""Agent responsible for researching and scraping content from the web."""

	def __init__(self, agent_id: str) -> None:
		super().__init__(agent_id)
		if not agent_config.llm or not agent_config.search_tool:
			msg = "AIModel must be initialized with an LLM and search tool before creating ResearchAgent"
			raise DataError(message=msg, status=422)
		self.research_agent = create_react_agent(
			name="research_agent",
			debug=settings.app.DEBUG,
			model=agent_config.llm,
			tools=[agent_config.search_tool],
			prompt=Prompts.RESEARCH_PROMPT,
		)

	async def execute(self, input_data: State) -> dict[str, Any]:
		if "initial_input" not in input_data or not input_data["initial_input"]:
			msg = "input_data must contain 'initial_input' with a course description"
			raise DataError(message=msg, status=422)

		result = await self.research_agent.ainvoke(
			{
				"messages": input_data.get("initial_input"),
			},
		)
		research_summary = result["messages"][-1].content

		return {"research_summary": research_summary}


research_agent = ResearchAgent("research_agent")
