from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from .agent import Agent
from .config.ai_config import agent_config
from .config.constants import State
from ..core import Prompts, settings
from ..errors import InitializationError
from ..errors.data_error import DataError


class OrganizerAgent(Agent):
	def __init__(self, agent_id: str):
		super().__init__(agent_id)
		if not agent_config.llm or not agent_config.search_tool:
			msg = "AIModel must be initialized with an LLM and search tool before creating OrganizerAgent"
			raise InitializationError(
				message=msg,
				status=502,
			)
		self.organizer_agent = create_react_agent(
			name="organizer_agent",
			debug=settings.app.DEBUG,
			model=agent_config.llm,
			tools=[],
			prompt=Prompts.ORGANIZER_PROMPT,
		)

	async def execute(self, input_data: State) -> dict[str, Any]:
		if "filtered_modules" not in input_data or not input_data["filtered_modules"]:
			msg = "input_data must contain 'filtered_modules' from FilterAgent"
			raise DataError(message=msg, status=422)

		result = await self.organizer_agent.ainvoke(
			{
				"messages": [
					HumanMessage(
						content=input_data.get("filtered_modules", ""),  # type:ignore
					),
				],
			},
		)
		organized_content = result["messages"][-1].content

		return {"organized_content": organized_content}


organizer_agent = OrganizerAgent("organizer_agent")
