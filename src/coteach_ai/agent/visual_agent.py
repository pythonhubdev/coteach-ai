from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from ..core import Prompts, settings
from ..errors import DataError, InitializationError
from .agent import Agent
from .config.ai_config import agent_config
from .config.constants import State


class VisualAgent(Agent):
	def __init__(self, agent_id: str):
		super().__init__(agent_id)
		if not agent_config.llm or not agent_config.search_tool:
			msg = "AIModel must be initialized with an LLM and search tool before creating VisualAgent"
			raise InitializationError(
				message=msg,
				status=500,
			)
		self.visual_agent = create_react_agent(
			name="visual_agent",
			debug=settings.app.DEBUG,
			model=agent_config.llm,
			tools=[agent_config.search_tool],
			prompt=Prompts.VISUAL_PROMPT,
		)

	async def execute(self, input_data: State) -> dict[str, Any]:
		if "organized_content" not in input_data or not input_data["organized_content"]:
			msg = "input_data must contain 'organized_content' from OrganizerAgent"
			raise DataError(message=msg, status=422)

		result = await self.visual_agent.ainvoke(
			{
				"messages": [
					HumanMessage(
						content=input_data.get("organized_content", ""),  # type:ignore
					),
				],
			},
		)
		visual_content = result["messages"][-1].content

		return {"visual_content": visual_content}


visual_agent = VisualAgent("visual_agent")
