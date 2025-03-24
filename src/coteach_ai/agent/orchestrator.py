import json
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from loguru import logger

from src.coteach_ai.core import settings

from ..errors import DataError
from .agent import State
from .filter_agent import filter_agent
from .organizer_agent import organizer_agent
from .research_agent import research_agent
from .visual_agent import visual_agent


class Orchestrator:
	def __init__(self) -> None:
		self.graph: CompiledStateGraph = self._build_graph()

	@staticmethod
	def _build_graph() -> CompiledStateGraph:  # noqa: C901
		builder = StateGraph(State)

		async def research_node(state: State) -> Command:
			update = await research_agent.run(state)
			return Command(update=update, goto="filter")

		async def filter_node(state: State) -> Command:
			update = await filter_agent.run(state)
			return Command(update=update, goto="organizer")

		async def organizer_node(state: State) -> Command:
			update = await organizer_agent.run(state)
			return Command(update=update, goto="visual")

		async def visual_node(state: State) -> Command:
			update = await visual_agent.run(state)
			return Command(update=update, goto="combine")

		def combine_node(state: State) -> Command:
			"""
			Combine JSON-formatted organized_content, visual_content, and research_summary into a final course structure.

			Args:
				state: Dictionary containing initial_input, organized_content, visual_content, and research_summary.

			Returns:
				Command object with the final course structure.

			Raises:
				DataError: If required fields are missing or input_content is malformed.

			"""
			logger.info(f"The current state is {state}")
			if not state.get("organized_content") or not state.get("visual_content"):
				raise DataError(
					message="State must contain 'organized_content' and 'visual_content' to combine",
					status=422,
				)

			organized_content: str = state.get("organized_content", "") or ""
			visual_content: str = state.get("visual_content", "") or ""
			research_summary: str = state.get("research_summary", "") or ""
			input_content: str | list[str | dict[str, Any]] = state["initial_input"][0].content

			assert isinstance(input_content, str), "input_content must be a string"
			if input_content.count("-") != 1:
				raise DataError(
					message="Input content must contain exactly one hyphen to separate brief and target audience",
					status=422,
				)
			unprocessed_brief, unprocessed_target_audience = input_content.split("-")
			brief = unprocessed_brief.replace("Brief: ", "").strip()
			target_audience = unprocessed_target_audience.replace("Target Audience: ", "").strip()

			topic = brief.split(" course")[0].replace("A ", "").capitalize()

			organized_dict = json.loads(organized_content)
			visual_dict = json.loads(visual_content)
			research_dict = json.loads(research_summary)

			references = [f"{ref['name']} - {ref['link']}" for ref in research_dict.get("references", [])]

			visual_resources = {module["title"]: module["lesson_resources"] for module in visual_dict["modules"]}

			modules = []
			for module in organized_dict["modules"]:
				module_title = module["title"]
				lessons = []
				lesson_resources = visual_resources.get(module_title, [])

				for idx, lesson in enumerate(module["lessons"]):
					title = lesson["title"]
					content = lesson["content"]
					existing_resources = lesson.get("resources", []).copy()

					if idx < len(lesson_resources):
						visual_url = lesson_resources[idx]["url"]
						existing_resources.append(visual_url)

					lessons.append({"title": title, "content": content, "resources": existing_resources})

				modules.append({"title": module_title, "lessons": lessons})

			combined_output = {
				"course_title": f"Introduction to {topic}",
				"description": f"A comprehensive introduction to {topic.lower()}, designed for {target_audience.lower()} with no prior knowledge.",
				"modules": modules,
				"references": references,
			}
			return Command(update={"final_course": combined_output}, goto=END)

		builder.add_node("researcher", research_node)
		builder.add_node("filter", filter_node)
		builder.add_node("organizer", organizer_node)
		builder.add_node("visual", visual_node)
		builder.add_node("combine", combine_node)
		builder.add_edge(START, "researcher")
		builder.add_edge("researcher", "filter")
		builder.add_edge("filter", "organizer")
		builder.add_edge("organizer", "visual")
		builder.add_edge("visual", "combine")
		builder.add_edge("combine", END)

		return builder.compile(debug=settings.app.DEBUG)

	async def run(self, brief: str, target_audience: str) -> dict[str, Any]:
		"""Run the orchestrator to generate a course from a description."""
		initial_state: State = {
			"initial_input": [
				HumanMessage(
					content=f"Brief: {brief} - Target Audience: {target_audience}",
				),
			],
			"research_summary": None,
			"filtered_modules": None,
			"organized_content": None,
			"visual_content": None,
			"final_course": None,
		}
		result = await self.graph.ainvoke(initial_state)
		return result["final_course"]


orchestrator = Orchestrator()
